import math

def compute_dislocation_forces(G=40e9, nu=0.3, b=2.86e-10, B_visc=1e-4):
    """
    Розрахунок сили взаємодії між двома паралельними крайовими дислокаціями
    та чисельне інтегрування траєкторії ковзання.
    """
    # Множник сили взаємодії
    C_force = (G * b**2) / (2.0 * math.pi * (1.0 - nu))
    r0_core = 2.0 * b  # Радіус згладжування ядра
    
    print(f"Константа взаємодії C_force = {C_force:.4e} Н/м")
    
    def force_x(x, y):
        r2 = x**2 + y**2 + r0_core**2
        return C_force * (x * (x**2 - y**2)) / (r2**2)

    # Тестові початкові конфігурації (x_0, y_0) для вільної дислокації D2
    test_positions = [
        (2.0e-9, 1.0e-9),   # x > y: відштовхування
        (0.5e-9, 1.0e-9),   # x < y: притягування до вертикальної стінки x=0
        (-1.5e-9, 1.0e-9),  # |x| > y (x < 0): F_x < 0, відштовхування ліворуч у бік -x
    ]
    
    dt = 1e-13  # крок інтегрування за часом (секунди)
    max_steps = 20000
    
    for idx, (x0, y0) in enumerate(test_positions, 1):
        x, y = x0, y0
        trajectory = [x]
        
        for step in range(max_steps):
            fx = force_x(x, y)
            vx = fx / B_visc
            
            x_next = x + vx * dt
            
            if abs(vx) < 1e-3 or abs(x_next - x) < 1e-15:
                break
                
            x = x_next
            trajectory.append(x)
            
        print(f"Конфігурація #{idx}: Старт x0 = {x0*1e9:.2f} нм, y0 = {y0*1e9:.2f} нм "
              f"-> Рівновага x_eq = {x*1e9:.4f} нм (кроків: {len(trajectory)})")

if __name__ == "__main__":
    compute_dislocation_forces()
