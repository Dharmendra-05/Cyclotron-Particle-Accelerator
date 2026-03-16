# Quick Start Guide

## Installation (2 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the main simulation
python main.py

# 3. View the generated plot
open cyclotron_trajectory.png  # macOS
# or
xdg-open cyclotron_trajectory.png  # Linux
```

**Done!** You'll see:
- Console output with simulation summary
- `cyclotron_trajectory.png` with the spiral trajectory colored by energy

---

## Explore Examples (5 minutes)

Run the parameter study examples:

```bash
python examples.py
```

This will generate:
- `example1_B_field_sweep.png` - How B field affects acceleration
- `example2_voltage_sweep.png` - How gap voltage affects acceleration  
- `example3_velocity_comparison.png` - Different starting velocities
- `example4_energy_conservation.png` - Energy conservation validation

---

## Customize Parameters

Edit `main.py` in the `main()` function:

```python
cyclotron = Cyclotron(
    B_field=1.5,           # Magnetic field (Tesla) - try 1.0, 2.0
    gap_voltage=50000,     # Accelerating voltage (Volts) - try 20000, 100000
    dee_radius=0.5,        # Dee radius (meters) - try 0.3, 1.0
    gap_width=0.01         # Gap width (meters)
)

results = cyclotron.simulate(
    t_span=(0, 1e-6),      # Simulation time (seconds) - try 2e-6, 5e-6
    initial_velocity=1e4,  # Starting speed (m/s) - try 1e5, 1e6
    num_points=5000,       # Plot resolution - try 10000 for smoother
    method='DOP853'        # ODE solver - try 'RK45' for faster
)
```

---

## Physics Highlights

1. **Spiral Trajectory**: Particle starts at center, spirals outward as it gains energy
2. **Color Gradient**: Blue/purple (low energy) → yellow (high energy)  
3. **Energy Gain**: Increases by ~50 keV per gap crossing
4. **Cyclotron Frequency**: ~144 MHz for 1.5 T field (proton)

See `README.md` for deep physics explanation!

---

## Typical Output

```
CYCLOTRON SIMULATION SUMMARY
============================================================
Magnetic Field:        1.500 T
Gap Voltage:           50.0 kV
Cyclotron Frequency:   143.682 MHz
Dee Radius:            50.0 cm
------------------------------------------------------------
Initial Kinetic Energy: 0.0000 MeV
Final Kinetic Energy:   2.1940 MeV
Energy Gain:            2.1940 MeV
Simulation Time:        1.000 μs
Number of Revolutions:  144
Final Orbital Radius:   13.98 cm
============================================================
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ImportError: No module named scipy | Run `pip install -r requirements.txt` |
| Simulation exits immediately | Increase `t_span` (e.g., `(0, 5e-6)`) |
| Plot looks blocky | Increase `num_points` (e.g., `10000`) |
| Memory error | Reduce `num_points` or `t_span` |
| Low final energy | Check gap voltage is in Volts (50000 = 50 kV) |

---

## Next Steps

1. **Understand the physics**: Read `README.md` for detailed explanations
2. **Modify parameters**: Change B field, voltage, dee radius
3. **Study the code**: `main.py` has detailed comments explaining each component
4. **Run examples**: `examples.py` shows parameter sweeps and validation
5. **Extend it**: Add relativistic effects, multiple particles, 3D visualization!

---

**Happy accelerating!** 🚀

For questions or contributions, see README.md
