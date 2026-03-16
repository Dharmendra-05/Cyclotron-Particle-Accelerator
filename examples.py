"""
Example: Cyclotron Parameter Studies
======================================

This script demonstrates how to use the Cyclotron class for parameter studies
and physics exploration.
"""

from main import Cyclotron
import numpy as np
import matplotlib.pyplot as plt


def example_1_varying_magnetic_field():
    """
    Example 1: How does magnetic field strength affect acceleration?
    
    A stronger magnetic field increases the cyclotron frequency, allowing
    more gap crossings in the same time window, resulting in higher final energy.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Effect of Magnetic Field Strength")
    print("="*70)
    
    B_values = [0.5, 1.0, 1.5, 2.0, 2.5]
    final_energies = []
    
    for B in B_values:
        cyclotron = Cyclotron(
            B_field=B,
            gap_voltage=50000,
            dee_radius=0.5
        )
        results = cyclotron.simulate(
            t_span=(0, 1e-6),
            initial_velocity=1e4,
            num_points=2000
        )
        final_energy = cyclotron.energy_profile[-1]
        final_energies.append(final_energy)
        
        print(f"B = {B:.1f} T  →  Final KE = {final_energy:.3f} MeV")
    
    # Plot results
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(B_values, final_energies, 'o-', linewidth=2, markersize=8, color='#1f77b4')
    ax.set_xlabel('Magnetic Field (T)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Final Kinetic Energy (MeV)', fontsize=12, fontweight='bold')
    ax.set_title('Cyclotron: Magnetic Field vs. Final Energy', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/example1_B_field_sweep.png', dpi=150)
    print("\n✓ Plot saved: example1_B_field_sweep.png\n")


def example_2_varying_gap_voltage():
    """
    Example 2: How does gap voltage affect acceleration?
    
    Higher voltage means more energy per gap crossing. Since ΔKE = q·V·N,
    doubling the voltage doubles the final energy (for the same number of crossings).
    """
    print("="*70)
    print("EXAMPLE 2: Effect of Gap Voltage")
    print("="*70)
    
    V_values = np.array([20, 40, 60, 80, 100]) * 1000  # Convert to Volts
    final_energies = []
    
    for V in V_values:
        cyclotron = Cyclotron(
            B_field=1.5,
            gap_voltage=V,
            dee_radius=0.5
        )
        results = cyclotron.simulate(
            t_span=(0, 1e-6),
            initial_velocity=1e4,
            num_points=2000
        )
        final_energy = cyclotron.energy_profile[-1]
        final_energies.append(final_energy)
        
        print(f"V = {V/1000:.0f} kV  →  Final KE = {final_energy:.3f} MeV")
    
    # Plot results
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(V_values/1000, final_energies, 's-', linewidth=2, markersize=8, color='#ff7f0e')
    ax.set_xlabel('Gap Voltage (kV)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Final Kinetic Energy (MeV)', fontsize=12, fontweight='bold')
    ax.set_title('Cyclotron: Gap Voltage vs. Final Energy', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/example2_voltage_sweep.png', dpi=150)
    print("\n✓ Plot saved: example2_voltage_sweep.png\n")


def example_3_trajectory_comparison():
    """
    Example 3: Compare trajectories for different initial velocities.
    
    Starting faster means the particle reaches the dee radius sooner,
    before it can be accelerated as much.
    """
    print("="*70)
    print("EXAMPLE 3: Effect of Initial Velocity")
    print("="*70)
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    v_initial_values = [1e4, 1e5, 5e5]  # m/s
    
    for idx, v0 in enumerate(v_initial_values):
        cyclotron = Cyclotron(
            B_field=1.5,
            gap_voltage=50000,
            dee_radius=0.5
        )
        results = cyclotron.simulate(
            t_span=(0, 1e-6),
            initial_velocity=v0,
            num_points=3000
        )
        
        # Extract trajectory
        x = cyclotron.trajectory[0] * 100  # cm
        y = cyclotron.trajectory[1] * 100
        
        # Plot
        ax = axes[idx]
        ax.plot(x, y, 'b-', linewidth=1.5, label='Trajectory')
        ax.plot(x[0], y[0], 'go', markersize=8, label='Start')
        ax.plot(x[-1], y[-1], 'r*', markersize=12, label='Exit')
        
        ax.set_xlabel('x (cm)', fontsize=11, fontweight='bold')
        ax.set_ylabel('y (cm)', fontsize=11, fontweight='bold')
        ax.set_title(f'v₀ = {v0:.0e} m/s', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        ax.legend(fontsize=9)
        
        print(f"v₀ = {v0:.0e} m/s  →  Final KE = {cyclotron.energy_profile[-1]:.3f} MeV")
    
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/example3_velocity_comparison.png', dpi=150)
    print("\n✓ Plot saved: example3_velocity_comparison.png\n")


def example_4_physics_validation():
    """
    Example 4: Validate conservation of energy and cyclotron physics.
    
    The magnetic force should not change kinetic energy; only the electric
    field should accelerate the particle.
    """
    print("="*70)
    print("EXAMPLE 4: Physics Validation - Energy Conservation")
    print("="*70)
    
    cyclotron = Cyclotron(
        B_field=1.5,
        gap_voltage=50000,
        dee_radius=0.5
    )
    results = cyclotron.simulate(
        t_span=(0, 1e-6),
        initial_velocity=1e4,
        num_points=5000
    )
    
    # Energy should increase monotonically
    energy = cyclotron.energy_profile
    
    # Check for negative energy changes (should be ~zero or positive)
    energy_changes = np.diff(energy)
    negative_changes = np.sum(energy_changes < -1e-6)
    
    print(f"Total energy gain: {energy[-1] - energy[0]:.4f} MeV")
    print(f"Number of negative energy steps: {negative_changes}")
    print(f"Min energy change: {energy_changes.min():.2e} MeV")
    print(f"Max energy change: {energy_changes.max():.2e} MeV")
    
    if negative_changes == 0:
        print("✓ Energy conservation validated: No unphysical energy loss!")
    else:
        print("⚠ Warning: Detected negative energy changes (may indicate numerical issues)")
    
    # Visualize energy monotonicity
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Energy vs time
    time_us = cyclotron.t_eval * 1e6
    ax1.plot(time_us, energy, 'b-', linewidth=2)
    ax1.set_xlabel('Time (μs)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Kinetic Energy (MeV)', fontsize=11, fontweight='bold')
    ax1.set_title('Energy vs. Time (Should be Monotonic)', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Energy change per step
    ax2.plot(time_us[:-1], energy_changes * 1e3, 'r-', linewidth=1.5, alpha=0.7)
    ax2.axhline(0, color='k', linestyle='--', alpha=0.3)
    ax2.set_xlabel('Time (μs)', fontsize=11, fontweight='bold')
    ax2.set_ylabel('ΔKE per step (keV)', fontsize=11, fontweight='bold')
    ax2.set_title('Energy Change Rate (Should be Non-Negative)', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('/mnt/user-data/outputs/example4_energy_conservation.png', dpi=150)
    print("\n✓ Plot saved: example4_energy_conservation.png\n")


if __name__ == '__main__':
    print("\n" + "█"*70)
    print("  CYCLOTRON SIMULATOR - PARAMETER STUDY EXAMPLES")
    print("█"*70)
    
    example_1_varying_magnetic_field()
    example_2_varying_gap_voltage()
    example_3_trajectory_comparison()
    example_4_physics_validation()
    
    print("="*70)
    print("All examples completed! Check /mnt/user-data/outputs/ for figures.")
    print("="*70 + "\n")
