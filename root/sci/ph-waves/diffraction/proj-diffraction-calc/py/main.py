# Python Implementation — Vectorized 2D Circular Airy Pattern Simulator
import numpy as np

def simulate_airy_disk_2d(wavelength=532e-9, diameter=1.0e-3, z_dist=1.5, grid_pts=512):
    """
    Моделювання двовимірної плями Ейрі при дифракції Фраунгофера на круглому отворі.
    """
    x = np.linspace(-0.005, 0.005, grid_pts)
    y = np.linspace(-0.005, 0.005, grid_pts)
    X, Y = np.meshgrid(x, y)
    R_screen = np.sqrt(X**2 + Y**2)
    
    sin_theta = R_screen / np.sqrt(R_screen**2 + z_dist**2)
    k = 2.0 * np.pi / wavelength
    q = k * (diameter / 2.0) * sin_theta
    
    # Використання граничного розкладу для уникнення ділення на нуль в центрі q = 0
    with np.errstate(divide='ignore', invalid='ignore'):
        from scipy.special import j1
        intensity = np.where(q == 0, 1.0, (2.0 * j1(q) / q)**2)
        
    return X, Y, intensity

if __name__ == '__main__':
    X, Y, I = simulate_airy_disk_2d()
    print(f"Розраховано двовимірну сітку {I.shape}. Максимальна інтенсивність у центрі = {I[256, 256]:.4f}")
