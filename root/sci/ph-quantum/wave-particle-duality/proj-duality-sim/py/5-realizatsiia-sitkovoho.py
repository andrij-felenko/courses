import numpy as np

def simulate_schrodinger_barrier(nodes=300, steps=6000):
    dx = 1.0e-11   # 0.01 нм
    dt = 1.0e-18   # 1 аттосекунда
    m_e = 9.109383e-31
    hbar = 1.054571e-34
    
    x = np.arange(nodes) * dx
    V = np.zeros(nodes)
    
    # Потенціальний бар'єр 10 eV
    barrier_mask = (x >= 160 * dx) & (x <= 170 * dx)
    V[barrier_mask] = 10.0 * 1.602176e-19
    
    x0 = 80 * dx
    sigma0 = 1.5e-10
    E_kin_J = 12.0 * 1.602176e-19
    k0 = np.sqrt(2.0 * m_e * E_kin_J) / hbar
    
    psi = np.exp(- (x - x0)**2 / (4 * sigma0**2)) * np.exp(1j * k0 * x)
    alpha = 1j * (hbar * dt) / (2.0 * m_e * dx**2)
    
    print("=== Сітковий симулятор тунелювання хвильового пакета (Python) ===")
    for step in range(steps + 1):
        if step % 2000 == 0:
            prob = np.abs(psi)**2
            mean_x = np.sum(x * prob) / np.sum(prob)
            norm = np.sum(prob) * dx
            print(f"Крок t = {step * dt * 1e15:5.1f} fs | Позиція x_avg = {mean_x * 1e9:.3f} нм | Норма = {norm:.4f}")
            
        psi_next = psi.copy()
        V_term = -1j * (dt / hbar) * V * psi
        psi_next[1:-1] = psi[1:-1] + alpha * (psi[2:] - 2*psi[1:-1] + psi[:-2]) + V_term[1:-1]
        psi = psi_next

if __name__ == "__main__":
    simulate_schrodinger_barrier()
