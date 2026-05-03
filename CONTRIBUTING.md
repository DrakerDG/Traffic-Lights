# ⚠️ Important Notes for Contributors

This project simulates two JetBot PROTO robots that can drive themselves with basic autonomy through a small town.

Please note the following restrictions before modifying the controller or the robots' behavior:

## Robot Configuration Restrictions

- The JetBot robots do not use distance sensors and/or lidar to detect obstacles while driving; they rely solely on basic computer vision.

- Excessive acceleration can cause:
  - The JetBot robots may not have enough time to detect red traffic lights.
  - Reduced or lost contact with the ground, potentially causing the wheels to skid.
  - Deviation from the intended path on curves.

---

# Contribution Philosophy

Contributions that:
- Improve image processing for road center detection and red light recognition are especially valued.
- Increase control robustness

without compromising physical realism or stability.

---

# Why This Matters

This repository is not only a simulation project, but also a control-systems learning platform that prioritizes:
- Deterministic behavior
- Realistic constraints
- Transferable control strategies

Please keep these goals in mind when proposing changes.
