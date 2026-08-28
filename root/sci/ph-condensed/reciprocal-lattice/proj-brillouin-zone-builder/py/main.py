import math
import numpy as np

class ReciprocalLattice:
    """Клас для обчислення векторів оберненої ґратки та зон Бріллюена."""
    
    def __init__(self, a1, a2, a3):
        self.a1 = np.array(a1, dtype=float)
        self.a2 = np.array(a2, dtype=float)
        self.a3 = np.array(a3, dtype=float)
        
        # Об'єм примітивної елементарної комірки прямого простору
        self.v_cell = float(np.dot(self.a1, np.cross(self.a2, self.a3)))
        if abs(self.v_cell) < 1e-12:
            raise ValueError("Базисні вектори прямої ґратки є компланарними!")
            
        # Формули Пауля Евальда для векторів оберненого базису
        self.b1 = (2.0 * math.pi / self.v_cell) * np.cross(self.a2, self.a3)
        self.b2 = (2.0 * math.pi / self.v_cell) * np.cross(self.a3, self.a1)
        self.b3 = (2.0 * math.pi / self.v_cell) * np.cross(self.a1, self.a2)

    def get_reciprocal_vector(self, h, k, l):
        """Обчислює вектор оберненої ґратки G[hkl] = h*b1 + k*b2 + l*b3."""
        return h * self.b1 + k * self.b2 + l * self.b3

    def interplanar_spacing(self, h, k, l):
        """Обчислює міжплощинну відстань d[hkl] = 2pi / |G[hkl]|."""
        g = self.get_reciprocal_vector(h, k, l)
        g_len = np.linalg.norm(g)
        if g_len < 1e-12:
            raise ValueError("Індекси Міллера не можуть бути одночасно нульовими!")
        return 2.0 * math.pi / g_len

    def is_inside_first_brillouin_zone(self, k_vec, max_index=2):
        """Перевіряє чи належить хвильовий вектор k першій зоні Бріллюена."""
        k_arr = np.array(k_vec, dtype=float)
        for h in range(-max_index, max_index + 1):
            for k in range(-max_index, max_index + 1):
                for l in range(-max_index, max_index + 1):
                    if h == 0 and k == 0 and l == 0:
                        continue
                    g = self.get_reciprocal_vector(h, k, l)
                    g_sq = np.dot(g, g)
                    # Перевірка умови Бреґґа: k . G <= 0.5 * |G|^2
                    if np.dot(k_arr, g) > 0.5 * g_sq + 1e-9:
                        return False
        return True

# Демонстраційний розрахунок для гранецентрованої кубічної ґратки (FCC Кремнію)
if __name__ == "__main__":
    a = 0.543  # параметр ґратки Si в нанометрах
    # Примітивні вектори трансляції FCC
    a1 = [0.0, a / 2.0, a / 2.0]
    a2 = [a / 2.0, 0.0, a / 2.0]
    a3 = [a / 2.0, a / 2.0, 0.0]

    lat = ReciprocalLattice(a1, a2, a3)
    print(f"Об'єм прямої примітивної комірки V_cell: {lat.v_cell:.5f} нм³")
    print(f"Міжплощинна відстань d(111): {lat.interplanar_spacing(1, 1, 1):.5f} нм")
    print(f"Міжплощинна відстань d(220): {lat.interplanar_spacing(2, 2, 0):.5f} нм")

    # Перевірка кристалографічних точок у k-просторі
    k_gamma = [0.0, 0.0, 0.0]
    k_boundary = lat.b1 * 0.5
    k_outside = lat.b1 * 0.8

    print(f"Точка Gamma (0,0,0) всередині ЗБ: {lat.is_inside_first_brillouin_zone(k_gamma)}")
    print(f"Точка на межі b1/2 всередині ЗБ: {lat.is_inside_first_brillouin_zone(k_boundary)}")
    print(f"Точка за межею 0.8*b1 всередині ЗБ: {lat.is_inside_first_brillouin_zone(k_outside)}")
