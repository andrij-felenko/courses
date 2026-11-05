"""
Модуль кінематики та розрахунку просторової жорсткості комбінованого підвісу під кутом 45 градусів.
"""

import math
from typing import Dict, Tuple


class SpatialMountModel:
    """
    Математична модель 3D-підвісу на комбінованих віброізоляторах (сталевий трос + силікон).
    """

    def __init__(
        self,
        wire_kc_n_m: float = 4500.0,
        wire_ks_n_m: float = 1800.0,
        silicone_kc_n_m: float = 2200.0,
        silicone_ks_n_m: float = 900.0,
        silicone_damping_c_ns_m: float = 12.0,
        tilt_angle_deg: float = 45.0,
        num_isolators: int = 4,
    ) -> None:
        self.k_comp_single = wire_kc_n_m + silicone_kc_n_m
        self.k_shear_single = wire_ks_n_m + silicone_ks_n_m
        self.c_single = silicone_damping_c_ns_m
        self.tilt_angle_deg = tilt_angle_deg
        self.num_isolators = num_isolators

    @property
    def tilt_angle_rad(self) -> float:
        return math.radians(self.tilt_angle_deg)

    def compute_single_mount_stiffness(self) -> Tuple[float, float]:
        """
        Декомпозиція жорсткості однієї похилої опори на вертикальну (Z) та поздовжню вісь нахилу:
        k_vert = k_comp * sin^2(theta) + k_shear * cos^2(theta)
        k_horiz = k_comp * cos^2(theta) + k_shear * sin^2(theta)
        """
        sin_a = math.sin(self.tilt_angle_rad)
        cos_a = math.cos(self.tilt_angle_rad)

        k_vert = self.k_comp_single * (sin_a ** 2) + self.k_shear_single * (cos_a ** 2)
        k_horiz = self.k_comp_single * (cos_a ** 2) + self.k_shear_single * (sin_a ** 2)
        return k_vert, k_horiz

    def get_total_stiffness(self) -> Dict[str, float]:
        """
        Сумарна жорсткість симетричного 4-опорного підвісу за осями X, Y, Z.
        """
        k_v_single, k_h_single = self.compute_single_mount_stiffness()
        k_z = self.num_isolators * k_v_single
        k_xy = (self.num_isolators / 2.0) * (k_h_single + self.k_shear_single)
        return {"x": k_xy, "y": k_xy, "z": k_z}

    def get_natural_frequency(self, mass_kg: float, axis: str = "z") -> float:
        """
        Власна резонансна частота f0 = 1 / (2 * pi) * sqrt(K / m).
        """
        if mass_kg <= 0:
            return 0.0
        k_tot = self.get_total_stiffness().get(axis.lower(), 1.0)
        omega_0 = math.sqrt(k_tot / mass_kg)
        return omega_0 / (2.0 * math.pi)

    def get_damping_ratio(self, mass_kg: float, axis: str = "z") -> float:
        """
        Коефіцієнт демпфування zeta = C_tot / (2 * sqrt(K_tot * m)).
        """
        if mass_kg <= 0:
            return 0.0
        k_tot = self.get_total_stiffness().get(axis.lower(), 1.0)
        c_tot = self.num_isolators * self.c_single
        return c_tot / (2.0 * math.sqrt(k_tot * mass_kg))
