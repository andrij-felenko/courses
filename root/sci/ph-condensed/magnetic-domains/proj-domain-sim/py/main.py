import random
import math

class MagneticDomainSimulator2D:
    """Чисельний симулятор магнітних доменів на 2D-сітці за методом Метрополіса."""
    
    def __init__(self, grid_size=50, J_exchange=1.0, temperature=1.5):
        self.size = grid_size
        self.J = J_exchange
        self.temp = temperature
        # Ініціалізація повністю хаотичного стану (+1 або -1 з ймовірністю 50%)
        self.grid = [
            [1 if random.random() > 0.5 else -1 for _ in range(self.size)]
            for _ in range(self.size)
        ]

    def _get_neighbors_sum(self, r, c):
        """Сума орієнтацій 4 найближчих сусідів із періодичними граничними умовами."""
        top = self.grid[(r - 1) % self.size][c]
        bottom = self.grid[(r + 1) % self.size][c]
        left = self.grid[r][(c - 1) % self.size]
        right = self.grid[r][(c + 1) % self.size]
        return top + bottom + left + right

    def monte_carlo_step(self, external_h=0.0):
        """Один повний крок Метрополіса (N*N випробувань перевороту)."""
        total_sites = self.size * self.size
        for _ in range(total_sites):
            r = random.randint(0, self.size - 1)
            c = random.randint(0, self.size - 1)
            spin = self.grid[r][c]
            
            neighbors_sum = self._get_neighbors_sum(r, c)
            # ΔE = 2 * S * (J * S_neighbors + H_ext)
            delta_energy = 2.0 * spin * (self.J * neighbors_sum + external_h)
            
            # Умова прийняття нового стану за Метрополісом
            if delta_energy <= 0.0 or random.random() < math.exp(-delta_energy / self.temp):
                self.grid[r][c] = -spin

    def get_magnetization(self):
        """Обчислення середньої питомої намагніченості M ∈ [-1.0, +1.0]."""
        total_spin = sum(sum(row) for row in self.grid)
        return total_spin / (self.size * self.size)

    def render_ascii_map(self):
        """Візуалізація доменної карти у текстовому консольному форматі."""
        print("=== КАРТА МАГНІТНИХ ДОМЕНІВ (# : +1, . : -1) ===")
        for row in self.grid:
            line = "".join("#" if s > 0 else "." for s in row)
            print(line)

if __name__ == "__main__":
    # Запуск симуляції на сітці 40x40 при T = 1.3 (нижче T_c ≈ 2.27)
    sim = MagneticDomainSimulator2D(grid_size=40, J_exchange=1.0, temperature=1.3)
    print(f"Початкова намагніченість M_0 = {sim.get_magnetization():.3f}")
    
    # Проведення 120 кроків Монте-Карло для релаксації до доменної структури
    for step in range(120):
        sim.monte_carlo_step(external_h=0.0)
    
    print(f"Кінцева намагніченість після релаксації M = {sim.get_magnetization():.3f}")
    sim.render_ascii_map()
