import math
import numpy as np

class Charge:
    """Клас для представлення точкового електричного заряду."""
    def __init__(self, q, x, y):
        self.q = q  # Величина заряду в Кулонах
        self.x = x  # Координата X в метрах
        self.y = y  # Координата Y в метрах

class FieldTracer2D:
    """Класичний чисельний трасувальник силових ліній електростатичного поля."""
    def __init__(self, charges, k_e=8.9875e9):
        self.charges = charges
        self.k_e = k_e

    def calc_field(self, x, y):
        """Обчислення вектора напруженості поля E = (Ex, Ey) у точці (x, y)."""
        ex, ey = 0.0, 0.0
        for c in self.charges:
            dx = x - c.x
            dy = y - c.y
            r2 = dx*dx + dy*dy
            r = math.sqrt(r2)
            if r < 1e-6:
                continue
            # E = k * q / r^2 вздовж одиничного вектора (dx/r, dy/r)
            e_mag = self.k_e * c.q / r2
            ex += e_mag * (dx / r)
            ey += e_mag * (dy / r)
        return ex, ey

    def get_unit_field(self, x, y, direction=1.0):
        """Нормований вектор напрямку силової лінії (із урахуванням знака напрямку)."""
        ex, ey = self.calc_field(x, y)
        emag = math.hypot(ex, ey)
        if emag < 1e-12:
            return 0.0, 0.0
        return direction * (ex / emag), direction * (ey / emag)

    def rk4_step(self, x, y, ds, direction=1.0):
        """Один крок алгоритму Рунге — Кутти 4-го порядку."""
        f1x, f1y = self.get_unit_field(x, y, direction)
        if f1x == 0.0 and f1y == 0.0:
            return x, y

        f2x, f2y = self.get_unit_field(x + 0.5*ds*f1x, y + 0.5*ds*f1y, direction)
        f3x, f3y = self.get_unit_field(x + 0.5*ds*f2x, y + 0.5*ds*f2y, direction)
        f4x, f4y = self.get_unit_field(x + ds*f3x, y + ds*f3y, direction)

        nx = x + (ds / 6.0) * (f1x + 2.0*f2x + 2.0*f3x + f4x)
        ny = y + (ds / 6.0) * (f1y + 2.0*f2y + 2.0*f3y + f4y)
        return nx, ny

    def trace_line(self, start_x, start_y, ds=0.01, max_steps=1500, 
                   bounds=(-1.5, 1.5, -1.5, 1.5), direction=1.0):
        """Трасування однієї силової лінії від початкової точки."""
        line = [(start_x, start_y)]
        cx, cy = start_x, start_y
        xmin, xmax, ymin, ymax = bounds
        r_cutoff = 0.035

        for _ in range(max_steps):
            nx, ny = self.rk4_step(cx, cy, ds, direction)
            
            # 1. Перевірка виходу за просторові межі розрахунку
            if not (xmin <= nx <= xmax and ymin <= ny <= ymax):
                break
                
            # 2. Перевірка потрапляння в окіл стоку/джерела
            hit_sink = False
            for c in self.charges:
                if math.hypot(nx - c.x, ny - c.y) < r_cutoff:
                    hit_sink = True
                    break
            if hit_sink:
                line.append((nx, ny))
                break

            line.append((nx, ny))
            cx, cy = nx, ny

        return line

    def generate_field_map(self, lines_per_charge=16, ds=0.008):
        """Генерація повної карти силових ліній для системи зарядів."""
        all_lines = []
        r_start = 0.045
        
        for c in self.charges:
            # Випромінюємо лінії з додатних зарядів за полем (+1.0)
            # та з від'ємних зарядів проти поля (-1.0)
            direction = 1.0 if c.q > 0 else -1.0
            num_lines = int(lines_per_charge * abs(c.q) / 1e-9)
            
            for i in range(num_lines):
                angle = 2.0 * math.pi * i / num_lines
                sx = c.x + r_start * math.cos(angle)
                sy = c.y + r_start * math.sin(angle)
                line = self.trace_line(sx, sy, ds=ds, direction=direction)
                all_lines.append(line)

        return all_lines

# Приклад виклику
if __name__ == "__main__":
    # Створюємо диполь: +1 нКл та -1 нКл
    charges = [
        Charge(1e-9, -0.4, 0.0),
        Charge(-1e-9, 0.4, 0.0)
    ]
    tracer = FieldTracer2D(charges)
    field_lines = tracer.generate_field_map(lines_per_charge=12)
    print(f"Успішно розраховано {len(field_lines)} силових ліній.")
