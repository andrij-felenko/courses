# thermal_expansion_sim.py — Python чисельне моделювання
import numpy as np

def simulate_lj_chain(temp, num_atoms=50, dt=0.002, steps=200000, therm_steps=50000):
    r0 = 2.0 ** (1.0 / 6.0)
    x = np.arange(num_atoms) * r0
    v = np.zeros(num_atoms)
    gamma = 1.0
    mass = 1.0
    noise_std = np.sqrt(2.0 * gamma * mass * temp / dt)
    
    def get_forces(pos):
        f = np.zeros(num_atoms)
        dr = pos[1:] - pos[:-1]
        dr = np.maximum(dr, 0.1)
        sr6 = (1.0 / dr) ** 6
        force = (24.0 / dr) * (2.0 * sr6**2 - sr6)
        f[:-1] -= force
        f[1:] += force
        return f

    f = get_forces(x)
    lengths = []
    
    for step in range(steps):
        R = np.random.normal(0, noise_std, num_atoms)
        v += 0.5 * dt * (f - gamma * v + R) / mass
        x += dt * v
        f = get_forces(x)
        R = np.random.normal(0, noise_std, num_atoms)
        v += 0.5 * dt * (f - gamma * v + R) / mass
        
        if step >= therm_steps:
            lengths.append(x[-1] - x[0])
            
    return np.mean(lengths)

if __name__ == "__main__":
    L0 = (50 - 1) * (2.0 ** (1.0 / 6.0))
    print(f"L0 (0 K) = {L0:.4f}")
    for T in [0.01, 0.05, 0.10, 0.20, 0.30]:
        L_avg = simulate_lj_chain(T)
        delta_pct = ((L_avg - L0) / L0) * 100.0;
        print(f"T = {T:.2f} -> L = {L_avg:.4f} (+{delta_pct:.3f}%)")
