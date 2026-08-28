import numpy as np

def simulate_huygens_diffraction(
    wavelength: float = 0.5e-6,   # 500 нм (зелене світло)
    slit_width: float = 5.0e-6,   # ширина щілини 5 мкм
    num_sources: int = 200,       # кількість вторинних джерел Гюйгенса
    screen_distance: float = 50e-6,# відстань до екрана 50 мкм
    screen_width: float = 80e-6,  # ширина екрана спостереження
    num_screen_pts: int = 400     # кількість точок розрахунку на екрані
):
    """
    Чисельне моделювання дифракції світла на щілині за принципом Гюйгенса-Кірхгофа.
    Повертає масив координат екрана (y_screen) та розподіл інтенсивності (intensity).
    """
    k = 2.0 * np.pi / wavelength
    
    # 1. Розміщення вторинних точкових джерел Гюйгенса у площині щілини (x = 0)
    y_sources = np.linspace(-slit_width / 2.0, slit_width / 2.0, num_sources)
    x_sources = np.zeros(num_sources)
    amplitude = 1.0 / num_sources
    
    # 2. Сітка точок спостереження на екрані (x = screen_distance)
    y_screen = np.linspace(-screen_width / 2.0, screen_width / 2.0, num_screen_pts)
    x_screen = np.full(num_screen_pts, screen_distance)
    
    intensity = np.zeros(num_screen_pts)
    
    # 3. Сумування комплексних амплітуд вторинних хвиль для кожної точки екрана
    eps = (wavelength / 20.0) ** 2
    for i in range(num_screen_pts):
        px, py = x_screen[i], y_screen[i]
        
        # Векторизований розрахунок відстаней та кутів від усіх джерел до точки P(px, py)
        dx = px - x_sources
        dy = py - y_sources
        r = np.sqrt(dx**2 + dy**2 + eps)
        
        cos_theta = dx / r
        # Фактор спрямованості Кірхгофа K(theta) = 0.5 * (1 + cos_theta)
        k_factor = 0.5 * (1.0 + cos_theta)
        
        # Комплексна амплітуда dE = (A / sqrt(r)) * K(theta) * exp(i * (k*r - pi/2))
        phase = k * r - (np.pi / 2.0)
        complex_field = (amplitude / np.sqrt(r)) * k_factor * (np.cos(phase) + 1j * np.sin(phase))
        
        total_field = np.sum(complex_field)
        intensity[i] = np.abs(total_field)**2
        
    # Нормування інтенсивності на максимум
    if np.max(intensity) > 0:
        intensity /= np.max(intensity)
        
    return y_screen, intensity

if __name__ == "__main__":
    y_scr, I_scr = simulate_huygens_diffraction()
    print(f"Розрахунок завершено. Отримано {len(I_scr)} точок профілю інтенсивності.")
    print(f"Центральна інтенсивність I(0) = {I_scr[len(I_scr)//2]:.4f}")
