import math, random

def robust_soliton(k, c=0.05, delta=0.5):
    p = [0.0] * (k + 1)                      # p[1..k]; p[0] не вживають
    p[1] = 1.0 / k                           # ідеальний солітон ρ
    for d in range(2, k + 1):
        p[d] = 1.0 / (d * (d - 1))
    R = c * math.log(k / delta) * math.sqrt(k)   # добавка τ і сплеск при ⌊k/R⌋
    kr = int(k / R)
    for d in range(1, kr):
        p[d] += R / (d * k)
    if kr >= 1:
        p[kr] += R * math.log(R / delta) / k
    beta = sum(p)
    return [x / beta for x in p]             # нормуємо → μ

def droplet_recipe(seed, k, mu):
    """Із самого зерна — степінь і набір індексів. Спільна для кодера й декодера."""
    rng = random.Random(seed)
    r, acc, d = rng.random(), 0.0, k
    for i in range(1, k + 1):               # вибір степеня за μ
        acc += mu[i]
        if r <= acc:
            d = i
            break
    return rng.sample(range(k), d)          # d РІЗНИХ індексів блоків

def xor_into(dst, src):                     # dst ^= src, побайтово
    for i in range(len(dst)):
        dst[i] ^= src[i]

class LTEncoder:
    def __init__(self, blocks, mu):
        self.blocks, self.k, self.mu = blocks, len(blocks), mu

    def droplet(self, seed):
        payload = bytearray(len(self.blocks[0]))
        for i in droplet_recipe(seed, self.k, self.mu):
            xor_into(payload, self.blocks[i])
        return seed, bytes(payload)         # на дроті: зерно + вантаж
