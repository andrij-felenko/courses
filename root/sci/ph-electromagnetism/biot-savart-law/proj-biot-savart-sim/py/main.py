import math

class Vector3:
    """Тривимірний вектор у декартовій системі координат."""
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __add__(self, o):
        return Vector3(self.x + o.x, self.y + o.y, self.z + o.z)

    def __sub__(self, o):
        return Vector3(self.x - o.x, self.y - o.y, self.z - o.z)

    def __mul__(self, s):
        return Vector3(self.x * s, self.y * s, self.z * s)

    def cross(self, o):
        return Vector3(
            self.y * o.z - self.z * o.y,
            self.z * o.x - self.x * o.z,
            self.x * o.y - self.y * o.x
        )

    def length(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

def compute_biot_savart(nodes, current, point):
    """Обчислення індукції B методом дискретизації Біо-Савара."""
    mu0 = 4.0 * math.pi * 1e-7
    factor = (mu0 * current) / (4.0 * math.pi)
    B = Vector3()

    for i in range(len(nodes) - 1):
        dl = nodes[i + 1] - nodes[i]
        r_mid = (nodes[i] + nodes[i + 1]) * 0.5
        R = point - r_mid
        dist = R.length()

        if dist < 1e-9:
            continue

        dist3 = dist**3
        dB = dl.cross(R) * (factor / dist3)
        B = B + dB

    return B

if __name__ == "__main__":
    radius = 0.1
    segments = 2000
    current = 10.0

    # Генерація вузлів витка
    loop = []
    for i in range(segments + 1):
        phi = 2.0 * math.pi * i / segments
        loop.append(Vector3(radius * math.cos(phi), radius * math.sin(phi), 0.0))

    point = Vector3(0.0, 0.0, 0.05)
    B = compute_biot_savart(loop, current, point)

    print("--- Результати чисельного розрахунку (Python) ---")
    print(f"B_x: {B.x * 1e6:.4f} uT")
    print(f"B_y: {B.y * 1e6:.4f} uT")
    print(f"B_z: {B.z * 1e6:.4f} uT (Очікуване: ~44.9639 uT)")
