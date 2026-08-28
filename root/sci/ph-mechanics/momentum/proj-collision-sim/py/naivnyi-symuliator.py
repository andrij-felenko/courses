from dataclasses import dataclass

@dataclass
class Body:
    x: float; v: float; m: float; r: float       # центр, швидкість, маса, півширина

def total_p(bodies):
    return sum(b.m * b.v for b in bodies)         # повний імпульс — наш свідок

def overlap(a, b):
    return abs(a.x - b.x) < a.r + b.r             # поверхні перекрилися

def approaching(a, b):
    return (b.x - a.x) * (b.v - a.v) < 0          # зближаються, а не вже розходяться

def step_fixed(bodies, dt, e=1.0):
    for b in bodies:
        b.x += b.v * dt                            # такт 1 · вільний проліт усіх тіл
    n = len(bodies)
    for i in range(n):
        for j in range(i + 1, n):                  # такт 2 · перебрати всі пари
            a, b = bodies[i], bodies[j]
            if overlap(a, b) and approaching(a, b):
                resolve(a, b, e)                   # такт 3 · розв'язати дотик
