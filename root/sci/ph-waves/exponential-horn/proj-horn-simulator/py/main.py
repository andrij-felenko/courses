import math
import cmath

def simulate_exponential_horn(d0_m, dL_m, fc_hz, c=343.0, rho=1.204, num_points=100):
    """
    Розрахунок геометрії та спектра вхідного імпедансу експоненційного рупора.
    Параметри:
      d0_m: діаметр горла в метрах
      dL_m: діаметр гирла в метрах
      fc_hz: частота зрізу в Герцах
      c: швидкість звуку в м/с
      rho: густина повітря в кг/м³
    """
    S0 = math.pi * (d0_m ** 2) / 4.0
    SL = math.pi * (dL_m ** 2) / 4.0
    
    # Показник розширення та необхідна розрахункова довжина
    m = (4.0 * math.pi * fc_hz) / c
    L = math.log(SL / S0) / m
    
    print(f"--- Параметри рупора ---")
    print(f"Площа горла S0: {S0*1e4:.2f} см²")
    print(f"Площа гирла SL: {SL*1e4:.2f} см²")
    print(f"Коефіцієнт розширення m: {m:.3f} м⁻¹")
    print(f"Розрахункова довжина L: {L*100:.2f} см")
    
    # Профіль рупора
    profile = []
    for i in range(num_points + 1):
        x = (L * i) / num_points
        S_x = S0 * math.exp(m * x)
        d_x = 2.0 * math.sqrt(S_x / math.pi)
        profile.append((x, d_x, S_x))
        
    # Спектр імпедансу нескінченного рупора
    freq_spectrum = []
    for i in range(1, 101):
        f = (3.0 * fc_hz * i) / 100.0
        if f >= fc_hz:
            r_norm = math.sqrt(1.0 - (fc_hz / f) ** 2)
            x_norm = fc_hz / f
        else:
            r_norm = 0.0
            x_norm = f / fc_hz
            
        z_norm = complex(r_norm, x_norm)
        z_abs = abs(z_norm)
        freq_spectrum.append((f, r_norm, x_norm, z_abs))
        
    return profile, freq_spectrum

if __name__ == '__main__':
    # Тестовий розрахунок для компресійного драйвера 1 дюйм (d0 = 0.0254 м)
    # та частоти зрізу fc = 400 Гц
    prof, spec = simulate_exponential_horn(d0_m=0.0254, dL_m=0.30, fc_hz=400.0)
    print("\nПриклад вхідного імпедансу на f = 800 Гц (f/fc = 2.0):")
    f_sample, r_val, x_val, _ = spec[50]
    print(f"Частота: {f_sample:.1f} Гц | R_norm: {r_val:.4f} | X_norm: {x_val:.4f}")
