import numpy as np

class PlasmaConfig:
    def __init__(self, R0=1.65, a=0.50, B0=2.50, Bpol0=0.30, m=3.34e-27, q=1.602e-19):
        self.R0 = R0
        self.a = a
        self.B0 = B0
        self.Bpol0 = Bpol0
        self.m = m
        self.q = q

def compute_velocities(R, Z, v_par, v_per, cfg):
    r = np.sqrt((R - cfg.R0)**2 + Z**2)
    r_safe = np.maximum(r, 1e-6)

    B_phi = cfg.B0 * cfg.R0 / R
    B_pol = cfg.Bpol0 * (r_safe / cfg.a)
    B_total = np.sqrt(B_phi**2 + B_pol**2)

    mu = (cfg.m * v_per**2) / (2.0 * B_total)
    v_drift_Z = (cfg.m * v_par**2 + mu * B_total) / (cfg.q * cfg.B0 * cfg.R0)

    v_rot_R = -v_par * (B_pol / B_total) * (Z / r_safe)
    v_rot_Z =  v_par * (B_pol / B_total) * ((R - cfg.R0) / r_safe)

    return v_rot_R, v_rot_Z + v_drift_Z

def simulate_trajectory(R_init=1.85, Z_init=0.0, v_par=5e5, v_per=7e5, dt=1e-8, steps=10000):
    cfg = PlasmaConfig()
    R, Z = R_init, Z_init
    trajectory = []

    for i in range(steps + 1):
        if i % 1000 == 0:
            trajectory.append((i, R, Z))

        # Метод Рунге-Кутти 4-го порядку (RK4)
        dR1, dZ1 = compute_velocities(R, Z, v_par, v_per, cfg)
        dR2, dZ2 = compute_velocities(R + 0.5*dt*dR1, Z + 0.5*dt*dZ1, v_par, v_per, cfg)
        dR3, dZ3 = compute_velocities(R + 0.5*dt*dR2, Z + 0.5*dt*dZ2, v_par, v_per, cfg)
        dR4, dZ4 = compute_velocities(R + dt*dR3, Z + dt*dZ3, v_par, v_per, cfg)

        R += (dt / 6.0) * (dR1 + 2.0*dR2 + 2.0*dR3 + dR4)
        Z += (dt / 6.0) * (dZ1 + 2.0*dZ2 + 2.0*dZ3 + dZ4)

    return trajectory

if __name__ == "__main__":
    traj = simulate_trajectory()
    print("Крок\tR (м)\t\tZ (м)")
    for step, R_val, Z_val in traj:
        print(f"{step}\t{R_val:.6f}\t{Z_val:.6f}")
