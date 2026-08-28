import numpy as np

class KelvinHelmholtzSolverPy:
    def __init__(self, nx=128, ny=128, lx=1.0, ly=1.0, nu=1e-4, dt=1e-3):
        self.nx = nx
        self.ny = ny
        self.lx = lx
        self.ly = ly
        self.dx = lx / nx
        self.dy = ly / ny
        self.nu = nu
        self.dt = dt
        
        self.w = np.zeros((ny, nx))  # Вихровість
        self.psi = np.zeros((ny, nx)) # Функція струменю
        self.u = np.zeros((ny, nx))   # Подовжня швидкість
        self.v = np.zeros((ny, nx))   # Поперечна швидкість
        
    def init_shear_layer(self, u0=1.0, delta=0.05, eps=0.05):
        y = np.linspace(-self.ly/2, self.ly/2, self.ny)
        x = np.linspace(0, self.lx, self.nx)
        X, Y = np.meshgrid(x, y)
        
        # Основний профіль швидкості U(y) = U0 * tanh(y / delta)
        u_base = u0 * np.tanh(Y / delta)
        v_pert = eps * u0 * np.sin(2 * np.pi * X / self.lx) * np.exp(-(Y / delta)**2)
        
        self.u = u_base
        self.v = v_pert
        
        # Обчислення початкової вихровості w = dv/dx - du/dy
        du_dy = np.gradient(self.u, self.dy, axis=0)
        dv_dx = np.gradient(self.v, self.dx, axis=1)
        self.w = dv_dx - du_dy

    def solve_poisson_jacobi(self, max_iter=200, tol=1e-5):
        """Розв'язок ∇²ψ = -w методом Якобі"""
        dx2 = self.dx**2
        dy2 = self.dy**2
        factor = 0.5 * (dx2 * dy2) / (dx2 + dy2)
        
        for _ in range(max_iter):
            psi_old = self.psi.copy()
            self.psi[1:-1, 1:-1] = factor * (
                (psi_old[1:-1, 2:] + psi_old[1:-1, :-2]) / dx2 +
                (psi_old[2:, 1:-1] + psi_old[:-2, 1:-1]) / dy2 +
                self.w[1:-1, 1:-1]
            )
            # Періодичні граничні умови за X
            self.psi[:, 0] = self.psi[:, -2]
            self.psi[:, -1] = self.psi[:, 1]
            
            if np.max(np.abs(self.psi - psi_old)) < tol:
                break
                
        # Оновлення швидкостей u = dψ/dy, v = -dψ/dx
        self.u[1:-1, :] = (self.psi[2:, :] - self.psi[:-2, :]) / (2 * self.dy)
        self.v[:, 1:-1] = -(self.psi[:, 2:] - self.psi[:, :-2]) / (2 * self.dx)

    def step(self):
        self.solve_poisson_jacobi()
        
        # Обчислення конвекції та дифузії вихровості
        dw_dx = np.gradient(self.w, self.dx, axis=1)
        dw_dy = np.gradient(self.w, self.dy, axis=0)
        d2w_dx2 = np.gradient(dw_dx, self.dx, axis=1)
        d2w_dy2 = np.gradient(dw_dy, self.dy, axis=0)
        
        convection = self.u * dw_dx + self.v * dw_dy
        diffusion = self.nu * (d2w_dx2 + d2w_dy2)
        
        # Крок за часом (Ейлер)
        self.w[1:-1, 1:-1] += self.dt * (-convection[1:-1, 1:-1] + diffusion[1:-1, 1:-1])
        
        # Періодичні умови за X
        self.w[:, 0] = self.w[:, -2]
        self.w[:, -1] = self.w[:, 1]

if __name__ == "__main__":
    sim = KelvinHelmholtzSolverPy(nx=64, ny=64)
    sim.init_shear_layer()
    for t in range(100):
        sim.step()
    print("Python KH simulation success. Max vorticity:", np.max(np.abs(sim.w)))
