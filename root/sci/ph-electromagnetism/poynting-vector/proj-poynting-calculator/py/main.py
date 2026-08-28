import math

class Vector3D:
    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def cross(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def dot(self, other: 'Vector3D') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def magnitude(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)


def poynting_coaxial_field(r_val: float, phi_val: float, v_volts: float, i_amps: float, a_m: float, b_m: float):
    """Обчислення полів E та H у точці (r, phi) у коаксіальному кабелі."""
    ln_ba = math.log(b_m / a_m)
    # Електричне поле E у радіальному напрямку r̂
    e_mag = v_volts / (r_val * ln_ba)
    e_vec = Vector3D(e_mag * math.cos(phi_val), e_mag * math.sin(phi_val), 0.0)

    # Магнітне поле H у азимутальному напрямку φ̂
    h_mag = i_amps / (2.0 * math.pi * r_val)
    h_vec = Vector3D(-h_mag * math.sin(phi_val), h_mag * math.cos(phi_val), 0.0)

    return e_vec, h_vec


def integrate_poynting_coaxial(v_volts: float, i_amps: float, a_m: float, b_m: float, n_r: int = 200, n_phi: int = 360) -> float:
    """Інтегрування вектора Пойнтінга по кільцевому перерізу коаксіального кабелю."""
    dr = (b_m - a_m) / n_r
    dphi = (2.0 * math.pi) / n_phi
    total_power = 0.0

    normal_z = Vector3D(0.0, 0.0, 1.0)  # Нормаль до перерізу уздовж осі Z

    for i in range(n_r):
        r_mid = a_m + (i + 0.5) * dr
        da = r_mid * dr * dphi  # Елемент площі кільця
        for j in range(n_phi):
            phi_mid = (j + 0.5) * dphi
            e_vec, h_vec = poynting_coaxial_field(r_mid, phi_mid, v_volts, i_amps, a_m, b_m)
            s_vec = e_vec.cross(h_vec)  # Вектор Пойнтінга S = E x H
            total_power += s_vec.dot(normal_z) * da

    return total_power


if __name__ == "__main__":
    v_val, i_val = 100.0, 2.0
    ra, rb = 0.002, 0.007
    power_calc = integrate_poynting_coaxial(v_val, i_val, ra, rb)
    power_theory = v_val * i_val

    print(f"Обчислена потужність: {power_calc:.4f} Вт")
    print(f"Теоретична потужність (V*I): {power_theory:.4f} Вт")
    print(f"Відносна похибка: {abs(power_calc - power_theory) / power_theory * 100:.6f}%")
