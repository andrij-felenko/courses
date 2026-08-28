import math


def dot(a, b):                     # скалярний добуток
    return a[0] * b[0] + a[1] * b[1]


def magnitude(a):                  # довжина = корінь з a·a
    return math.sqrt(dot(a, a))


def angle_between(a, b):           # кут між векторами у радіанах
    c = dot(a, b) / (magnitude(a) * magnitude(b))
    c = max(-1.0, min(1.0, c))     # затиск проти похибки округлення,
    return math.acos(c)            # інакше acos кине ValueError
