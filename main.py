"""
Cyclotron Particle Accelerator Simulation
==========================================

A high-fidelity simulation of a cyclotron particle accelerator using the Lorentz force
equations and resonant acceleration via alternating electric fields.

Author: Physics Simulation Team
Version: 1.0
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
import scipy.integrate as integrate
from typing import Tuple, Dict, List
from dataclasses import dataclass


@dataclass
class PhysicalConstants:
    """Physical constants in SI units."""
    proton_charge: float = 1.602176634e-19  # Coulombs
    proton_mass: float = 1.67262192369e-27  # kg
    speed_of_light: float = 299792458  # m/s


class Cyclotron:
    """
    A cyclotron particle accelerator simulator.
    
    This class simulates the motion of a proton in a cyclotron under the Lorentz force,
    with resonant acceleration at each crossing of the accelerating gap.
    
    Attributes:
        B_field (float): Magnetic field strength in Tesla (z-direction)
        gap_voltage (float): Accelerating voltage across the gap in Volts
        dee_radius (float): Radius of the circular dees in meters
        gap_width (float): Width of the accelerating gap in meters
        constants (PhysicalConstants): Physical constants
    """
    
    def __init__(
        self,
        B_field: float = 1.5,
        gap_voltage: float = 50000,
        dee_radius: float = 0.5,
        gap_width: float = 0.01,
        constants: PhysicalConstants = None
    ):
        """
        Initialize the cyclotron.
        
        Args:
            B_field: Magnetic field strength (Tesla)
            gap_voltage: Accelerating voltage (Volts)
            dee_radius: Radius of the circular dees (meters)
            gap_width: Width of accelerating gap (meters)
            constants: Physical constants (uses defaults if None)
        """
        self.B_field = B_field
        self.gap_voltage = gap_voltage
        self.dee_radius = dee_radius
        self.gap_width = gap_width
        self.constants = constants or PhysicalConstants()
        
        # Derived quantities
        self.q = self.constants.proton_charge
        self.m = self.constants.proton_mass
        self.cyclotron_frequency = self._calculate_cyclotron_frequency()
        
        # Simulation state
        self.trajectory = None
        self.t_eval = None
        self.energy_profile = None
        
    def _calculate_cyclotron_frequency(self) -> float:
        """Calculate the cyclotron frequency ω_c = qB/m in rad/s."""
        return self.q * self.B_field / self.m
    
    def _lorentz_force(self, t: float, state: np.ndarray) -> np.ndarray:
        """
        Calculate the Lorentz force and return acceleration.
        
        F = q(E + v × B)
        a = F/m = (q/m)(E + v × B)
        
        Args:
            t: Current time (seconds)
            state: [x, y, z, vx, vy, vz] - position and velocity
            
        Returns:
            State derivative: [vx, vy, vz, ax, ay, az]
        """
        x, y, z, vx, vy, vz = state
        
        # Velocity magnitude and kinetic energy
        v_mag = np.sqrt(vx**2 + vy**2 + vz**2)
        
        # Magnetic field (uniform, pointing in +z direction)
        B_vec = np.array([0, 0, self.B_field])
        
        # v × B (Lorentz force from magnetic field)
        v_vec = np.array([vx, vy, vz])
        v_cross_B = np.cross(v_vec, B_vec)
        
        # Electric field: only active in the gap, alternating at cyclotron frequency
        E_vec = self._get_electric_field(x, y, z, t)
        
        # Total acceleration: a = (q/m)(E + v × B)
        a_vec = (self.q / self.m) * (E_vec + v_cross_B)
        
        # Return state derivatives: [dx/dt, dy/dt, dz/dt, dvx/dt, dvy/dt, dvz/dt]
        return np.array([vx, vy, vz, a_vec[0], a_vec[1], a_vec[2]])
    
    def _get_electric_field(self, x: float, y: float, z: float, t: float) -> np.ndarray:
        """
        Get the electric field at position (x, y, z) and time t.
        
        The field is localized to the gap (between the two dees) and alternates
        at the cyclotron frequency to provide resonant acceleration.
        
        Args:
            x, y, z: Position
            t: Time
            
        Returns:
            Electric field vector [Ex, Ey, Ez]
        """
        E_vec = np.array([0.0, 0.0, 0.0])
        
        # Check if particle is in the gap region (y ≈ 0, within gap_width)
        if abs(y) < self.gap_width / 2:
            # Alternating field at cyclotron frequency
            # Field direction: along +y or -y depending on sign of cos(ω_c * t)
            field_magnitude = self.gap_voltage / self.gap_width
            
            # Phase: accelerate when particle crosses (cos term ensures proper phasing)
            phase = np.cos(self.cyclotron_frequency * t)
            
            # Electric field points in +y or -y
            E_vec[1] = field_magnitude * phase
        
        return E_vec
    
    def get_kinetic_energy(self, velocity: np.ndarray) -> float:
        """
        Calculate kinetic energy from velocity in MeV.
        
        KE = (1/2)mv² converted to MeV
        """
        v_mag = np.linalg.norm(velocity)
        KE_joules = 0.5 * self.m * v_mag**2
        KE_MeV = KE_joules / (1.602176634e-13)  # 1 MeV = 1.602e-13 J
        return KE_MeV
    
    def simulate(
        self,
        t_span: Tuple[float, float] = (0, 1e-6),
        initial_velocity: float = 1e4,
        num_points: int = 10000,
        method: str = 'RK45'
    ) -> Dict:
        """
        Run the cyclotron simulation using scipy's solve_ivp.
        
        Args:
            t_span: Time span as (t_start, t_end) in seconds
            initial_velocity: Initial speed of the proton in m/s
            num_points: Number of evaluation points for dense output
            method: ODE solver method ('RK45', 'RK23', 'DOP853', etc.)
            
        Returns:
            Dictionary with simulation results (trajectory, energy, time)
        """
        # Initial conditions: particle starts at center with initial_velocity in +x direction
        # Position: (0, 0, 0) - at the gap center
        # Velocity: (initial_velocity, 0, 0) - moving in +x direction
        state_0 = np.array([0, 0, 0, initial_velocity, 0, 0])
        
        # Create event to stop simulation when particle reaches dee_radius
        def radius_limit(t, state):
            x, y, z = state[:3]
            radius = np.sqrt(x**2 + y**2)
            return self.dee_radius - radius
        
        radius_limit.terminal = True
        radius_limit.direction = -1  # Trigger when radius increases past limit
        
        # Solve ODE
        print(f"[INFO] Running cyclotron simulation with {method} solver...")
        sol = integrate.solve_ivp(
            self._lorentz_force,
            t_span,
            state_0,
            method=method,
            dense_output=True,
            events=radius_limit,
            max_step=1e-9,
            rtol=1e-9,
            atol=1e-12
        )
        
        print(f"[INFO] Simulation complete. Status: {sol.status}")
        print(f"[INFO] Integration time: {sol.t[-1]:.3e} seconds")
        
        # Generate dense output for plotting
        self.t_eval = np.linspace(sol.t[0], sol.t[-1], num_points)
        sol_dense = sol.sol(self.t_eval)
        
        # Extract trajectory
        self.trajectory = sol_dense[:3]  # x, y, z positions
        velocities = sol_dense[3:]  # vx, vy, vz
        
        # Calculate energy profile
        self.energy_profile = np.array([
            self.get_kinetic_energy(velocities[:, i])
            for i in range(len(self.t_eval))
        ])
        
        return {
            't': self.t_eval,
            'trajectory': self.trajectory,
            'velocities': velocities,
            'energy': self.energy_profile,
            'solver_status': sol.status
        }
    
    def plot_trajectory(self, figsize: Tuple[int, int] = (14, 10), save_path: str = None):
        """
        Create a publication-quality plot of the cyclotron trajectory.
        
        The spiral is colored by kinetic energy (MeV) to show acceleration.
        
        Args:
            figsize: Figure size as (width, height)
            save_path: Optional path to save the figure
        """
        if self.trajectory is None:
            raise ValueError("No simulation data. Run simulate() first.")
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # --- Left panel: Main trajectory with energy colormap ---
        x = self.trajectory[0] * 100  # Convert to cm for display
        y = self.trajectory[1] * 100
        
        # Normalize energy for colormap
        norm = Normalize(vmin=self.energy_profile.min(), vmax=self.energy_profile.max())
        cmap = plt.cm.plasma
        
        # Plot trajectory segments with color gradient
        for i in range(len(x) - 1):
            color = cmap(norm(self.energy_profile[i]))
            ax1.plot(x[i:i+2], y[i:i+2], color=color, linewidth=1.5, zorder=1)
        
        # Plot starting point
        ax1.plot(x[0], y[0], 'go', markersize=10, label='Start', zorder=3)
        # Plot ending point
        ax1.plot(x[-1], y[-1], 'r*', markersize=15, label='Exit', zorder=3)
        
        # Add magnetic field indicator
        ax1.text(
            0.02, 0.98, f'B = {self.B_field:.2f} T (⊙ out of page)',
            transform=ax1.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        )
        
        ax1.set_xlabel('x (cm)', fontsize=12, fontweight='bold')
        ax1.set_ylabel('y (cm)', fontsize=12, fontweight='bold')
        ax1.set_title('Cyclotron Particle Trajectory', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.set_aspect('equal')
        ax1.legend(loc='upper right', fontsize=10)
        
        # Colorbar for energy
        sm = ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar1 = plt.colorbar(sm, ax=ax1, label='Kinetic Energy (MeV)')
        
        # --- Right panel: Energy vs. Radius ---
        radius = np.sqrt(x**2 + y**2)
        ax2.plot(radius, self.energy_profile, 'b-', linewidth=2, label='KE')
        ax2.fill_between(radius, self.energy_profile, alpha=0.3)
        
        ax2.set_xlabel('Orbital Radius (cm)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Kinetic Energy (MeV)', fontsize=12, fontweight='bold')
        ax2.set_title('Energy Gain During Acceleration', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend(fontsize=10)
        
        # Add physics info
        final_energy = self.energy_profile[-1]
        final_radius = radius[-1]
        ax2.text(
            0.05, 0.95,
            f'Final KE: {final_energy:.2f} MeV\nFinal r: {final_radius:.2f} cm',
            transform=ax2.transAxes, fontsize=10,
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5)
        )
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"[INFO] Figure saved to {save_path}")
        
        plt.show()
    
    def print_summary(self):
        """Print a summary of the simulation results."""
        if self.trajectory is None:
            print("No simulation data available.")
            return
        
        print("\n" + "="*60)
        print("CYCLOTRON SIMULATION SUMMARY")
        print("="*60)
        print(f"Magnetic Field:        {self.B_field:.3f} T")
        print(f"Gap Voltage:           {self.gap_voltage/1e3:.1f} kV")
        print(f"Cyclotron Frequency:   {self.cyclotron_frequency/1e6:.3f} MHz")
        print(f"Dee Radius:            {self.dee_radius*100:.1f} cm")
        print("-"*60)
        
        x = self.trajectory[0]
        y = self.trajectory[1]
        radius = np.sqrt(x**2 + y**2)
        
        print(f"Initial Kinetic Energy: {self.energy_profile[0]:.4f} MeV")
        print(f"Final Kinetic Energy:   {self.energy_profile[-1]:.4f} MeV")
        print(f"Energy Gain:            {self.energy_profile[-1] - self.energy_profile[0]:.4f} MeV")
        print(f"Simulation Time:        {self.t_eval[-1]*1e6:.3f} μs")
        print(f"Number of Revolutions:  {int(np.degrees(np.arctan2(y[-1], x[-1])) / 360)}")
        print(f"Final Orbital Radius:   {radius[-1]*100:.2f} cm")
        print(f"Exit Velocity:          {np.sqrt(self.trajectory[0][-1]**2 + self.trajectory[1][-1]**2):.3e} m/s")
        print("="*60 + "\n")


def main():
    """Main execution function."""
    
    # Create cyclotron with realistic parameters
    cyclotron = Cyclotron(
        B_field=1.5,           # 1.5 Tesla
        gap_voltage=50000,     # 50 kV
        dee_radius=0.5,        # 50 cm
        gap_width=0.01         # 1 cm
    )
    
    # Run simulation
    results = cyclotron.simulate(
        t_span=(0, 1e-6),      # 1 microsecond
        initial_velocity=1e4,  # 10 km/s
        num_points=5000,
        method='DOP853'        # High-order method for accuracy
    )
    
    # Print summary
    cyclotron.print_summary()
    
    # Create publication-quality plot
    cyclotron.plot_trajectory(
        figsize=(14, 6),
        save_path='cyclotron_trajectory.png'
    )


if __name__ == '__main__':
    main()
