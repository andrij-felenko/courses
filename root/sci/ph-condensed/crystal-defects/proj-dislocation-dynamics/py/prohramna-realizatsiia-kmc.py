import random
import math

class VacancyDiffusionKMC:
    """
    Симуляція випадкового блукання поодинокої вакансії у квадратній 2D ґратці
    методом Кінетичного Монте-Карло (Residence-Time Algorithm).
    """
    def __init__(self, lattice_size=100, T=800, E_m=0.8, nu0=1e13, a=2.86e-10):
        self.size = lattice_size
        self.T = T
        self.E_m = E_m          # Енергія міграції (еВ)
        self.nu0 = nu0          # Частота коливань (1/с)
        self.a = a              # Постійна ґратки (м)
        self.kB = 8.61733e-5    # Постійна Больцмана (еВ/К)
        
        self.vx = lattice_size // 2
        self.vy = lattice_size // 2
        
        self.moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        
    def calculate_rates(self):
        rate = self.nu0 * math.exp(-self.E_m / (self.kB * self.T))
        return [rate] * 4

    def run_simulation(self, total_jumps=100000):
        rates = self.calculate_rates()
        gamma_total = sum(rates)
        
        current_time = 0.0
        start_x, start_y = self.vx * self.a, self.vy * self.a
        
        # Нерозгорнуті координати для точного розрахунку переміщення
        unwrapped_x, unwrapped_y = start_x, start_y
        
        for step in range(total_jumps):
            u1 = random.random()
            while u1 == 0:
                u1 = random.random()
            dt = -math.log(u1) / gamma_total
            current_time += dt
            
            u2 = random.random() * gamma_total
            cum_rate = 0.0
            chosen_move = 0
            for idx, r in enumerate(rates):
                cum_rate += r
                if u2 <= cum_rate:
                    chosen_move = idx
                    break
                    
            dx, dy = self.moves[chosen_move]
            self.vx = (self.vx + dx) % self.size
            self.vy = (self.vy + dy) % self.size
            
            unwrapped_x += dx * self.a
            unwrapped_y += dy * self.a
            
        r2_displacement = (unwrapped_x - start_x)**2 + (unwrapped_y - start_y)**2
        D_simulated = r2_displacement / (4.0 * current_time)
        D_theoretical = (self.a**2 / 4.0) * gamma_total
        
        print(f"=== Результати KMC симуляції дифузії вакансії ===")
        print(f"Температура T              = {self.T} K")
        print(f"Загальний фізичний час      = {current_time:.6e} с")
        print(f"Кількість перескоків        = {total_jumps}")
        print(f"Розрахований D (симуляція) = {D_simulated:.4e} м²/с")
        print(f"Теоретичний D (аналітичний) = {D_theoretical:.4e} м²/с")
        
        return current_time, D_simulated

if __name__ == "__main__":
    kmc = VacancyDiffusionKMC(T=900, E_m=0.75)
    kmc.run_simulation(total_jumps=100000)
