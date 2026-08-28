import math

class GrapheneBandSimulator:
    """
    Клас для обчислення зонної структури графена методом сильного зв'язку (Tight-Binding).
    """
    def __init__(self, bond_length=0.142, hopping_integral=2.7):
        self.a_cc = bond_length  # Відстань між атомами C-C у нанометрах
        self.t = hopping_integral # Інтеграл перескоку найближчих сусідів у еВ

    def get_high_symmetry_points(self):
        """
        Повертає координати високосиметричних точок Gamma, K, M у k-просторі (1/нм).
        """
        pi = math.pi
        a_cc = self.a_cc

        gamma = (0.0, 0.0)
        k_point = (2.0 * pi / (3.0 * a_cc * math.sqrt(3.0)), 2.0 * pi / (3.0 * a_cc))
        m_point = (0.0, 2.0 * pi / (3.0 * a_cc))

        return gamma, k_point, m_point

    def interpolate_path(self, p1, p2, num_steps):
        """
        Лінійна інтерполяція між двома точками у k-просторі.
        """
        points = []
        for i in range(num_steps):
            alpha = i / float(num_steps)
            kx = p1[0] + alpha * (p2[0] - p1[0])
            ky = p1[1] + alpha * (p2[1] - p1[1])
            points.append((kx, ky))
        return points

    def compute_energy_at_k(self, kx, ky):
        """
        Обчислення комплексного структурного фактора f(k) та власних значень енергії.
        """
        a_cc = self.a_cc
        t = self.t

        # Фазові аргументи експонент
        arg1 = ky * a_cc
        arg2 = -ky * a_cc / 2.0
        arg3 = kx * a_cc * math.sqrt(3.0) / 2.0

        # Дійсна та уявна частини функції перескоку f(k)
        re_f = -t * (math.cos(arg1) + 2.0 * math.cos(arg2) * math.cos(arg3))
        im_f = -t * (math.sin(arg1) + 2.0 * math.sin(arg2) * math.cos(arg3))

        mod_f = math.sqrt(re_f * re_f + im_f * im_f)

        e_valence = -mod_f    # Зона pi (валентна)
        e_conduction = +mod_f # Зона pi* (провідність)

        return e_valence, e_conduction

    def run_simulation(self, steps_per_segment=100):
        """
        Запуск повного розрахунку уздовж контуру Gamma -> K -> M -> Gamma.
        """
        gamma, k_pt, m_pt = self.get_high_symmetry_points()

        path_gk = self.interpolate_path(gamma, k_pt, steps_per_segment)
        path_km = self.interpolate_path(k_pt, m_pt, steps_per_segment)
        path_mg = self.interpolate_path(m_pt, gamma, steps_per_segment)

        full_k_path = path_gk + path_km + path_mg
        band_data = []

        for kx, ky in full_k_path:
            e_v, e_c = self.compute_energy_at_k(kx, ky)
            band_data.append({'kx': kx, 'ky': ky, 'e_val': e_v, 'e_con': e_c})

        return band_data

if __name__ == "__main__":
    sim = GrapheneBandSimulator(bond_length=0.142, hopping_integral=2.7)
    results = sim.run_simulation(steps_per_segment=50)

    print(f"Розрахунок завершено. Отримано {len(results)} точок зонного спектра.")
    print("Аналіз характерних точок:")
    print(f"  1. Точка Gamma (k=0): E_val = {results[0]['e_val']:.4f} eV, E_con = {results[0]['e_con']:.4f} eV")
    print(f"  2. Точка K (Dirac):   E_val = {results[50]['e_val']:.4f} eV, E_con = {results[50]['e_con']:.4f} eV")
    print(f"  3. Точка M:           E_val = {results[100]['e_val']:.4f} eV, E_con = {results[100]['e_con']:.4f} eV")
