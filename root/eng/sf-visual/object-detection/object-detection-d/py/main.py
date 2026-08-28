import math

# контур — список точок (x, y)

# площа замкненого контуру (формула шнурівки) і периметр
def contour_geom(c):
    n = len(c)
    A = P = 0.0
    for i in range(n):
        (ax, ay), (bx, by) = c[i], c[(i + 1) % n]
        A += ax * by - bx * ay                          # шнурівка (Гаусса)
        P += math.hypot(bx - ax, by - ay)               # довжина сторони
    return abs(A) * 0.5, P

def is_circle(c, min_area):
    if len(c) < 5:                                       # замало точок на коло
        return False
    A, P = contour_geom(c)
    if A < min_area or P <= 0.0:                         # шум або вироджений контур
        return False
    circularity = 4.0 * math.pi * A / (P * P)
    return circularity > 0.85                            # близько до ідеального кола
