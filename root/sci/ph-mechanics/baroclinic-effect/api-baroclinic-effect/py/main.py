import numpy as np

class BaroclinicDiagnostic:
    def __init__(self, dx: float, dy: float, dz: float, latitude: float = 45.0):
        self.dx = dx
        self.dy = dy
        self.dz = dz
        self.latitude = latitude
        self.f0 = 2.0 * 7.2921159e-5 * np.sin(np.radians(latitude))
        self.g = 9.80665

    def compute_torque(self, p: np.ndarray, rho: np.ndarray) -> np.ndarray:
        """Обчислює бароклінний момент τ_z на 3D масивах."""
        drho_dx = np.gradient(rho, self.dx, axis=2)
        drho_dy = np.gradient(rho, self.dy, axis=1)
        dp_dx   = np.gradient(p,   self.dx, axis=2)
        dp_dy   = np.gradient(p,   self.dy, axis=1)
        
        return (drho_dx * dp_dy - drho_dy * dp_dx) / (rho ** 2)

    def compute_thermal_wind(self, T: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Обчислює вертикальний зсув геострофічного вітру (du_g/dz, dv_g/dz)."""
        dT_dx = np.gradient(T, self.dx, axis=2)
        dT_dy = np.gradient(T, self.dy, axis=1)
        
        du_g_dz = - (self.g / (self.f0 * T)) * dT_dy
        dv_g_dz =   (self.g / (self.f0 * T)) * dT_dx
        return du_g_dz, dv_g_dz
