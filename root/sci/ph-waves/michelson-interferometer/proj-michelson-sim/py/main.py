import math
import sys

def simulate_michelson(width=64, height=32, wavelength_nm=632.8, 
                       delta_L_um=10.0, wedge_angle_urad=15.0, R_mm=500.0):
    """
    Чисельне моделювання інтерференційної картини інтерферометра Майкельсона.
    
    Параметри:
      width, height       — розміри текстової сітки в пікселях
      wavelength_nm       — довжина хвилі лазера в нанометрах (632.8 нм = He-Ne)
      delta_L_um          — різниця довжин плечей у мікрометрах (d0)
      wedge_angle_urad    — кут клина між дзеркалами у мікрорадіанах (alpha)
      R_mm                — радіус кривизни хвильового фронту в міліметрах
    """
    wavelength = wavelength_nm * 1e-9      # переведення в метри
    d0 = delta_L_um * 1e-6                 # переведення в метри
    alpha = wedge_angle_urad * 1e-6        # переведення в радіани
    R = R_mm * 1e-3                        # переведення в метри
    w0 = 0.003                             # радіус лазерного пучка (3 мм)

    # Таблиця градацій яскравості для текстового відображення
    ASCII_CHARS = " .:-=+*#%@"
    
    grid = []
    scale_x = 0.006 / width   # фізичне охоплення по горизонталі: -3 мм .. +3 мм
    scale_y = 0.006 / height  # фізичне охоплення по вертикалі: -3 мм .. +3 мм

    for py in range(height):
        y = (py - height / 2.0) * scale_y
        row = []
        for px in range(width):
            x = (px - width / 2.0) * scale_x
            
            # Оптична різниця ходу Delta_s(x, y)
            delta_s = 2.0 * (d0 + alpha * x + (x**2 + y**2) / (2.0 * R))
            
            # Гаусовий профіль інтенсивності пучка
            gaussian = math.exp(-2.0 * (x**2 + y**2) / (w0**2))
            
            # Розрахунок інтерференційної інтенсивності I(x, y)
            phase = (math.pi * delta_s) / wavelength
            intensity = (math.cos(phase) ** 2) * gaussian
            
            # Квантування інтенсивності в індекс символу
            char_idx = int(intensity * (len(ASCII_CHARS) - 1))
            char_idx = max(0, min(len(ASCII_CHARS) - 1, char_idx))
            row.append(ASCII_CHARS[char_idx])
        grid.append("".join(row))
    
    return grid

def simulate_duplet_interferogram(max_delay_um=500.0, steps=10):
    """
    Моделювання згасання видності смуг для дублету натрію (589.0 нм та 589.6 нм).
    """
    lambda1 = 589.0e-9
    lambda2 = 589.6e-9
    results = []
    
    for i in range(steps):
        d = (i / float(steps)) * max_delay_um * 1e-6
        # Сума інтенсивностей двох спектральних ліній
        i1 = math.cos(2.0 * math.pi * 2.0 * d / lambda1) ** 2
        i2 = math.cos(2.0 * math.pi * 2.0 * d / lambda2) ** 2
        i_total = 0.5 * (i1 + i2)
        results.append((d * 1e6, i_total))
        
    return results

if __name__ == "__main__":
    print("=== Моделювання смуг Фізо (клин alpha = 20 мкрад) ===")
    pattern_fizeau = simulate_michelson(wedge_angle_urad=20.0, R_mm=10000.0)
    for line in pattern_fizeau:
        print(line)

    print("\n=== Моделювання кілець Гайдінгера (паралельні дзеркала, R = 300 мм) ===")
    pattern_haidinger = simulate_michelson(wedge_angle_urad=0.0, R_mm=300.0)
    for line in pattern_haidinger:
        print(line)

    print("\n=== Розрахунок видності смуг для дублету Натрію (589.0/589.6 нм) ===")
    duplet_data = simulate_duplet_interferogram(max_delay_um=300.0, steps=10)
    for d_um, vis in duplet_data:
        print(f"Зсув d = {d_um:6.1f} мкм | Відносна інтенсивність I = {vis:.3f}")
