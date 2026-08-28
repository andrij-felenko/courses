import numpy as np

class AnisotropySimulatorPy:
    """Чисельний симулятор мікромагнітної енергії та петель гістерезису."""
    def __init__(self, K1=4.5e5, Ms=1.4e6, name="Cobalt (Co)"):
        self.name = name
        self.K1 = K1
        self.Ms = Ms
        self.mu0 = 4.0 * np.pi * 1e-7
        self.HA = (2.0 * K1) / (self.mu0 * Ms)

    def energy_density(self, theta, hx, hz):
        """Безрозмірна потенціальна енергія e(theta)."""
        return 0.5 * np.sin(theta)**2 - hz * np.cos(theta) - hx * np.sin(theta)

    def d_energy(self, theta, hx, hz):
        """Перша похідна de/dtheta."""
        return np.sin(theta) * np.cos(theta) + hz * np.sin(theta) - hx * np.cos(theta)

    def d2_energy(self, theta, hx, hz):
        """Друга похідна d2e/dtheta2 (стійкість станів)."""
        return np.cos(2.0 * theta) + hz * np.cos(theta) + hx * np.sin(theta)

    def find_equilibrium(self, theta_init, hx, hz):
        """Гібридний пошук рівноважного кута намагніченості."""
        theta = theta_init
        for _ in range(60):
            g = self.d_energy(theta, hx, hz)
            h = self.d2_energy(theta, hx, hz)
            if abs(g) < 1e-8 and h > 0.0:
                return theta
            if abs(h) < 1e-12:
                h = 1e-6 if h >= 0 else -1e-6
            theta -= g / h

        # Сканування сітки при провалі ітерацій
        grid = np.linspace(0, 2 * np.pi, 720)
        stable_mask = self.d2_energy(grid, hx, hz) > 0.0
        if not np.any(stable_mask):
            return theta_init
        stable_grid = grid[stable_mask]
        energies = self.energy_density(stable_grid, hx, hz)
        return stable_grid[np.argmin(energies)]

    def compute_astroid(self, points=200):
        """Обчислення параметричних координат астроїди Стонера — Вольфарта."""
        t = np.linspace(0, 2 * np.pi, points)
        hx = np.sin(t)**3
        hz = np.cos(t)**3
        return hx, hz

    def simulate_hysteresis(self, theta_H_deg, steps=100):
        """Розрахунок петель m_parallel(h) та m_perp(h)."""
        theta_H = np.radians(theta_H_deg)
        h_forward = np.linspace(2.0, -2.0, steps)
        h_backward = np.linspace(-2.0, 2.0, steps)
        h_all = np.concatenate([h_forward, h_backward])

        m_par = []
        m_perp = []
        cur_theta = 0.0 if np.cos(theta_H) >= 0.0 else np.pi

        for h in h_all:
            hx = h * np.sin(theta_H)
            hz = h * np.cos(theta_H)
            cur_theta = self.find_equilibrium(cur_theta, hx, hz)
            m_par.append(np.cos(cur_theta - theta_H))
            m_perp.append(np.sin(cur_theta - theta_H))

        return h_all, np.array(m_par), np.array(m_perp)

if __name__ == "__main__":
    sim = AnisotropySimulatorPy()
    print(f"Матеріал: {sim.name}")
    print(f"Поле анізотропії HA: {sim.HA / 1e3:.2f} кА/м")
    
    hx_ast, hz_ast = sim.compute_astroid(8)
    print("\nВибірка точок астроїди (hx, hz):")
    for x, z in zip(hx_ast, hz_ast):
        print(f"  hx: {x:7.3f} | hz: {z:7.3f}")

    h_arr, m_par, m_perp = sim.simulate_hysteresis(45.0, steps=5)
    print("\nВибірка петлі гістерезису (θ_H = 45°):")
    for h, mp, mpe in zip(h_arr[:5], m_par[:5], m_perp[:5]):
        print(f"  h: {h:6.2f} | m_par: {mp:6.3f} | m_perp: {mpe:6.3f}")
