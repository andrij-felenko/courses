import math
import random


def gauss():
    """Нескінченний потік N(0, 1): по одному числу на next()."""
    while True:
        u1 = random.random()                 # рівномірне у [0, 1)
        u2 = 1.0 - random.random()           # рівномірне у (0, 1]: нуль під ln не випаде
        theta = 2.0 * math.pi * u1
        R     = math.sqrt(-2.0 * math.log(u2))
        yield R * math.cos(theta)            # z₁ — зараз
        yield R * math.sin(theta)            # z₂ — пара віддається наступним next()
