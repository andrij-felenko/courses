import math
from dataclasses import dataclass

@dataclass(frozen=True)
class Quaternion:
    w: float = 1.0
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def dot(self, other: "Quaternion") -> float:
        return self.w * other.w + self.x * other.x + self.y * other.y + self.z * other.z

    def norm(self) -> float:
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def normalized(self) -> "Quaternion":
        mag = self.norm()
        if mag < 1e-12:
            return Quaternion(1.0, 0.0, 0.0, 0.0)
        return Quaternion(self.w / mag, self.x / mag, self.y / mag, self.z / mag)

    @staticmethod
    def slerp(q1: "Quaternion", q2: "Quaternion", t: float) -> "Quaternion":
        dot = q1.dot(q2)

        # Вибір найкоротшого шляху на 3-сфері S3
        if dot < 0.0:
            dot = -dot
            q2 = Quaternion(-q2.w, -q2.x, -q2.y, -q2.z)

        # Захист від похибок заокруглення floating point
        dot = max(-1.0, min(1.0, dot))

        # Захист від ділення на нуль при малих кутах
        if dot > 0.9995:
            res = Quaternion(
                q1.w + t * (q2.w - q1.w),
                q1.x + t * (q2.x - q1.x),
                q1.y + t * (q2.y - q1.y),
                q1.z + t * (q2.z - q1.z)
            )
            return res.normalized()

        omega = math.acos(dot)
        sin_omega = math.sin(omega)
        scale1 = math.sin((1.0 - t) * omega) / sin_omega
        scale2 = math.sin(t * omega) / sin_omega

        return Quaternion(
            scale1 * q1.w + scale2 * q2.w,
            scale1 * q1.x + scale2 * q2.x,
            scale1 * q1.y + scale2 * q2.y,
            scale1 * q1.z + scale2 * q2.z
        )

if __name__ == "__main__":
    q_start = Quaternion(1.0, 0.0, 0.0, 0.0)
    theta_half = math.pi / 4.0
    q_end = Quaternion(math.cos(theta_half), 0.0, 0.0, math.sin(theta_half))

    print("Інтерполяція орієнтацій Python:")
    for step in range(5):
        t_val = step * 0.25
        qt = Quaternion.slerp(q_start, q_end, t_val)
        print(f"t = {t_val:.2f} -> (w: {qt.w:.4f}, x: {qt.x:.4f}, y: {qt.y:.4f}, z: {qt.z:.4f})")
