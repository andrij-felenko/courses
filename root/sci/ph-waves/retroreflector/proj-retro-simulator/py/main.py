import math

class Vector3:
    def __init__(self, x, y, z):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def length(self):
        return math.sqrt(self.dot(self))

    def normalize(self):
        l = self.length()
        if l == 0:
            return Vector3(0, 0, 0)
        return Vector3(self.x / l, self.y / l, self.z / l)

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

class MirrorPlane:
    def __init__(self, point, normal):
        self.point = point
        self.normal = normal.normalize()

    def intersect(self, ray_pos, ray_dir):
        denom = ray_dir.dot(self.normal)
        if abs(denom) < 1e-9:
            return None  # Промінь паралельний площині
        t = (self.point - ray_pos).dot(self.normal) / denom
        if t > 1e-6:
            return t
        return None

def reflect(v, n):
    return v - n * (2.0 * v.dot(n))

def trace_corner_cube(ray_pos, ray_dir, mirrors, max_bounces=3):
    current_pos = ray_pos
    current_dir = ray_dir.normalize()
    last_mirror_idx = -1

    for bounce in range(max_bounces):
        best_t = float('inf')
        hit_idx = -1

        for i, m in enumerate(mirrors):
            if i == last_mirror_idx:
                continue
            t = m.intersect(current_pos, current_dir)
            if t is not None and t < best_t:
                best_t = t
                hit_idx = i

        if hit_idx == -1:
            break

        current_pos = current_pos + current_dir * best_t
        n = mirrors[hit_idx].normal
        current_dir = reflect(current_dir, n)
        last_mirror_idx = hit_idx

    return current_pos, current_dir

def main():
    # Ідеальні три взаємно перпендикулярні грані куточка
    n1 = Vector3(1, 0, 0)
    n2 = Vector3(0, 1, 0)
    n3 = Vector3(0, 0, 1)
    origin = Vector3(0, 0, 0)

    mirrors = [
        MirrorPlane(origin, n1),
        MirrorPlane(origin, n2),
        MirrorPlane(origin, n3)
    ]

    # Вхідний промінь, що падає всередину куточка
    v_in = Vector3(-1, -1, -1).normalize()
    p_in = Vector3(2.0, 1.5, 1.8)

    p_out, v_out = trace_corner_cube(p_in, v_in, mirrors)

    target_dir = -v_in
    cos_angle = max(-1.0, min(1.0, v_out.dot(target_dir)))
    dev_rad = math.acos(cos_angle)
    dev_arcsec = math.degrees(dev_rad) * 3600.0

    print(f"Вхідний напрямок: ({v_in.x:.4f}, {v_in.y:.4f}, {v_in.z:.4f})")
    print(f"Вихідний напрямок: ({v_out.x:.4f}, {v_out.y:.4f}, {v_out.z:.4f})")
    print(f"Кутове відхилення від -v_in: {dev_arcsec:.4f} кутових секунд")

if __name__ == "__main__":
    main()
