import math

# Поворот вектора (x, y) на кут theta (радіани) проти годинникової стрілки.
def rotate2(x, y, theta):
    c = math.cos(theta)
    s = math.sin(theta)
    return (
        x * c - y * s,   # перший рядок матриці
        x * s + y * c,   # другий рядок матриці
    )
