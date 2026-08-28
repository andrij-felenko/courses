import math

class RayTracer:
    """Чисельний оптичний трасувальник для сферичної заломлювальної поверхні."""
    def __init__(self, radius: float, n1: float, n2: float):
        self.R = radius
        self.n1 = n1
        self.n2 = n2
        self.z_paraxial = (n2 * radius) / (n2 - n1)

    def trace_ray(self, y0: float) -> dict:
        """Трасування одного променя з початковою висотою y0."""
        if abs(y0) >= abs(self.R):
            raise ValueError("Висота променя перевищує радіус сферичної поверхні")

        # Крок 1: Точка перетину зі сферою
        z_surf = self.R - math.sqrt(self.R**2 - y0**2)
        
        # Крок 2-3: Заломлення за Снеллом
        sin_alpha = y0 / self.R
        sin_theta2 = (self.n1 / self.n2) * sin_alpha
        
        if abs(sin_theta2) > 1.0:
            raise ArithmeticError("Повне внутрішнє відбиття: промінь не заломлюється")
            
        theta2 = math.asin(sin_theta2)
        alpha = math.asin(sin_alpha)
        
        # Крок 4: Кут з віссю
        u_prime = alpha - theta2
        
        # Крок 5: Координата фокуса
        if abs(u_prime) < 1e-12:
            z_focus = self.z_paraxial
        else:
            z_focus = z_surf + y0 / math.tan(u_prime)

        ds_prime = z_focus - self.z_paraxial
        return {
            "y0": y0,
            "z_surf": z_surf,
            "z_focus": z_focus,
            "ds_prime": ds_prime,
            "u_prime_deg": math.degrees(u_prime)
        }

def main():
    tracer = RayTracer(radius=100.0, n1=1.0, n2=1.5)
    print(f"Параксіальний фокус z_p = {tracer.z_paraxial:.4f} мм\n")
    print(f"{'y0 (мм)':>8} | {'z_surf (мм)':>11} | {'z_focus (мм)':>12} | {'δs\' (мм)':>10} | {'U\' (град)':>10}")
    print("-" * 64)
    
    for y in [5.0, 10.0, 20.0, 30.0, 40.0, 50.0]:
        res = tracer.trace_ray(y)
        print(f"{res['y0']:8.1f} | {res['z_surf']:11.4f} | {res['z_focus']:12.4f} | {res['ds_prime']:10.4f} | {res['u_prime_deg']:10.4f}")

if __name__ == "__main__":
    main()
