import math

class ElectrostaticSolver2D:
    def __init__(self, nx: int, ny: int, h: float, eps_r: float = 1.0):
        self.nx = nx
        self.ny = ny
        self.h = h
        self.eps0 = 8.854187817e-12
        self.eps = self.eps0 * eps_r
        
        # Сітки потенціалу V, заряду rho та маски фіксованих вузлів
        self.v = [[0.0 for _ in range(ny)] for _ in range(nx)]
        self.rho = [[0.0 for _ in range(ny)] for _ in range(nx)]
        self.is_fixed = [[False for _ in range(ny)] for _ in range(nx)]

    def set_boundary_electrode(self, x_min: int, x_max: int, y: int, voltage: float):
        """Встановлення металевого електрода (умова Діріхле)."""
        for i in range(x_min, x_max + 1):
            self.v[i][y] = voltage
            self.is_fixed[i][y] = True

    def solve_poisson(self, max_iter: int = 5000, tol: float = 1e-6, omega: float = 1.85) -> int:
        """Метод послідовної верхньої релаксації (SOR) для ∇²V = -rho/eps."""
        h2 = self.h * self.h
        for iteration in range(max_iter):
            max_diff = 0.0
            for i in range(1, self.nx - 1):
                for j in range(1, self.ny - 1):
                    if self.is_fixed[i][j]:
                        continue
                    
                    v_new = 0.25 * (self.v[i+1][j] + self.v[i-1][j] + 
                                   self.v[i][j+1] + self.v[i][j-1] + 
                                   (h2 * self.rho[i][j] / self.eps))
                    
                    # Релаксаційний зсув
                    v_sor = self.v[i][j] + omega * (v_new - self.v[i][j])
                    diff = abs(v_sor - self.v[i][j])
                    if diff > max_diff:
                        max_diff = diff
                    self.v[i][j] = v_sor
            
            if max_diff < tol:
                return iteration + 1
        return max_iter

    def compute_field_energy(self, depthz: float = 1.0) -> float:
        """Обчислення повної енергії поля W = ∫ (1/2 * eps * E²) dV."""
        total_energy = 0.0
        inv_2h = 1.0 / (2.0 * self.h)
        cell_vol = self.h * self.h * depthz
        
        for i in range(1, self.nx - 1):
            for j in range(1, self.ny - 1):
                # Центрально-різницевий градієнт поля E = -grad(V)
                ex = -(self.v[i+1][j] - self.v[i-1][j]) * inv_2h
                ey = -(self.v[i][j+1] - self.v[i][j-1]) * inv_2h
                
                e_sq = ex * ex + ey * ey
                w_e = 0.5 * self.eps * e_sq
                total_energy += w_e * cell_vol
                
        return total_energy

# Приклад використання:
if __name__ == "__main__":
    nx, ny = 100, 100
    h = 0.001  # 1 мм крок сітки
    solver = ElectrostaticSolver2D(nx, ny, h, eps_r=2.2)  # поліпропілен
    
    # Створення пластин конденсатора на відстані 20 мм (20 клітинок)
    solver.set_boundary_electrode(20, 80, 40, voltage=100.0)  # Верхня пластина +100 В
    solver.set_boundary_electrode(20, 80, 60, voltage=0.0)    # Нижня пластина 0 В
    
    iters = solver.solve_poisson()
    w_field = solver.compute_field_energy(depthz=0.1)  # 10 см глибина
    
    print(f"Збіжність за {iters} ітерацій.")
    print(f"Обчислена енергія поля: {w_field * 1e6:.4f} мкДж")
