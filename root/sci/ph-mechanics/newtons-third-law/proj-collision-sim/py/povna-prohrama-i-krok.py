m  = [1.0, 3.0, 2.0]              # маси, кг
x  = [0.0, 2.0, 5.0]             # координати, м
v  = [4.0, 0.0, -1.0]            # швидкості, м/с
k, d0, dt = 200.0, 1.0, 0.002    # жорсткість Н/м, діаметр дотику м, крок с

def total_momentum():
    return sum(m[i] * v[i] for i in range(len(m)))

P0 = total_momentum()
worst = 0.0
for _ in range(1200):
    F = pair_forces(x, k, d0)
    for i in range(len(m)):
        v[i] += F[i] / m[i] * dt     # a = F/m — другий закон
    for i in range(len(m)):
        x[i] += v[i] * dt            # рушаємо тіла вже новою швидкістю
    worst = max(worst, abs(total_momentum() - P0))

print(P0, total_momentum(), worst)
