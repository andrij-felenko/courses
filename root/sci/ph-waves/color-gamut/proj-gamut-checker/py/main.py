# Python: реалізація Gamut Checker та компресії кольору

class Vector3:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

class GamutChecker:
    # Обернена матриця sRGB D65
    M_INV_SRGB = [
        [ 3.2404542, -1.5371385, -0.4985314],
        [-0.9692660,  1.8760108,  0.0415560],
        [ 0.0556434, -0.2040259,  1.0572252]
    ]

    def __init__(self, r_xy=(0.64, 0.33), g_xy=(0.30, 0.60), b_xy=(0.15, 0.06), w_xy=(0.3127, 0.3290)):
        self.r = r_xy
        self.g = g_xy
        self.b = b_xy
        self.w = w_xy

    @staticmethod
    def xyz_to_srgb(xyz: Vector3) -> Vector3:
        """Перетворення XYZ у лінійні sRGB."""
        m = GamutChecker.M_INV_SRGB
        r = m[0][0]*xyz.x + m[0][1]*xyz.y + m[0][2]*xyz.z
        g = m[1][0]*xyz.x + m[1][1]*xyz.y + m[1][2]*xyz.z
        b = m[2][0]*xyz.x + m[2][1]*xyz.y + m[2][2]*xyz.z
        return Vector3(r, g, b)

    def is_in_gamut(self, xyz: Vector3) -> bool:
        """Перевірка, чи належить колір sRGB охопленню."""
        rgb = self.xyz_to_srgb(xyz)
        eps = 1e-6
        return (-eps <= rgb.x <= 1.0 + eps and
                -eps <= rgb.y <= 1.0 + eps and
                -eps <= rgb.z <= 1.0 + eps)

    def clip_to_gamut(self, xyz: Vector3) -> Vector3:
        """Жорсткий кліпінг лінійних RGB значений."""
        rgb = self.xyz_to_srgb(xyz)
        clamped_r = max(0.0, min(1.0, rgb.x))
        clamped_g = max(0.0, min(1.0, rgb.y))
        clamped_b = max(0.0, min(1.0, rgb.z))
        return Vector3(clamped_r, clamped_g, clamped_b)

    def compress_desaturate(self, xy: tuple[float, float], steps: int = 50) -> tuple[float, float]:
        """Перцептивний зсув до білої точки D65 до потрапляння всередину трикутника."""
        px, py = xy
        wx, wy = self.w
        
        def cross_product(p1, p2, p3):
            return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])

        def in_triangle(pt):
            d1 = cross_product(pt, self.r, self.g)
            d2 = cross_product(pt, self.g, self.b)
            d3 = cross_product(pt, self.b, self.r)
            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            return not (has_neg and has_pos)

        if in_triangle((px, py)):
            return (px, py)

        low, high = 0.0, 1.0
        best_x, best_y = wx, wy
        for _ in range(steps):
            t = (low + high) / 2.0
            cur_x = px * (1.0 - t) + wx * t
            cur_y = py * (1.0 - t) + wy * t
            if in_triangle((cur_x, cur_y)):
                best_x, best_y = cur_x, cur_y
                high = t
            else:
                low = t

        return (best_x, best_y)

if __name__ == "__main__":
    checker = GamutChecker()
    laser_xyz = Vector3(0.14, 0.03, 0.85)
    print("Належить sRGB:", checker.is_in_gamut(laser_xyz))
    clipped = checker.clip_to_gamut(laser_xyz)
    print(f"Clipped RGB: ({clipped.x:.3f}, {clipped.y:.3f}, {clipped.z:.3f})")
