import math

def riemann_siegel_theta(t: float) -> float:
    """Обчислення фазового кута θ(t) за асимптотичною формулою Рімана-Зігеля."""
    if t < 0.1:
        return 0.0
    t_2pi = t / (2.0 * math.pi)
    return (t / 2.0) * math.log(t_2pi) - (t / 2.0) - (math.pi / 8.0) + (1.0 / (48.0 * t))

def hardy_z(t: float) -> float:
    """Обчислення дійснозначної функції Харді Z(t)."""
    theta = riemann_siegel_theta(t)
    bound = int(math.sqrt(t / (2.0 * math.pi)))
    if bound < 1:
        bound = 1
    
    z_sum = 0.0
    for n in range(1, bound + 1):
        z_sum += (1.0 / math.sqrt(n)) * math.cos(theta - t * math.log(n))
    
    return 2.0 * z_sum

def find_zeros(t_min: float, t_max: float, step: float = 0.1, tol: float = 1e-7):
    """Пошук нулів Z(t) методом бісекції."""
    zeros = []
    t_curr = t_min
    z_curr = hardy_z(t_curr)
    
    while t_curr < t_max:
        t_next = t_curr + step
        z_next = hardy_z(t_next)
        
        # Перевірка зміни знаку (зміна знаку розкриває наявність нуля)
        if z_curr * z_next < 0:
            # Метод бісекції
            low, high = t_curr, t_next
            for _ in range(50):
                mid = (low + high) / 2.0
                z_mid = hardy_z(mid)
                if abs(z_mid) < tol or (high - low) / 2.0 < tol:
                    zeros.append(mid)
                    break
                if z_curr * z_mid < 0:
                    high = mid
                else:
                    low = mid
                    z_curr = z_mid
        
        t_curr = t_next
        z_curr = z_next
    
    return zeros

if __name__ == "__main__":
    print("Пошук перших нетривіальних нулів Дзета-функції Рімана на Re(s) = 1/2:")
    found_zeros = find_zeros(10.0, 30.0, step=0.1)
    for i, z in enumerate(found_zeros, 1):
        print(f"Нуль #{i}: t = {z:.6f}  => s = 1/2 + i·{z:.6f}")
