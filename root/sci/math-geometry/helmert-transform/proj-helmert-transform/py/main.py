from dataclasses import dataclass
from enum import Enum
import math
import numpy as np

ARCSEC_TO_RAD = 4.8481368110953599e-6

class HelmertConvention(Enum):
    POSITION_VECTOR = "PositionVector"  # EPSG: 9606
    COORDINATE_FRAME = "CoordinateFrame"  # EPSG: 9607

@dataclass
class Helmert7:
    tx: float = 0.0  # м
    ty: float = 0.0  # м
    tz: float = 0.0  # м
    rx: float = 0.0  # кутові секунди
    ry: float = 0.0  # кутові секунди
    rz: float = 0.0  # кутові секунди
    s_ppm: float = 0.0  # ppm (10^-6)
    convention: HelmertConvention = HelmertConvention.POSITION_VECTOR

    def forward(self, p: np.ndarray) -> np.ndarray:
        p = np.asarray(p, dtype=float)
        sign = -1.0 if self.convention == HelmertConvention.COORDINATE_FRAME else 1.0
        rx = self.rx * ARCSEC_TO_RAD * sign
        ry = self.ry * ARCSEC_TO_RAD * sign
        rz = self.rz * ARCSEC_TO_RAD * sign
        s = self.s_ppm * 1e-6

        # Лінеаризована матриця (1 + s) * R
        rot = np.array([
            [1.0 + s, -(1.0 + s) * rz,  (1.0 + s) * ry],
            [(1.0 + s) * rz,  1.0 + s, -(1.0 + s) * rx],
            [-(1.0 + s) * ry, (1.0 + s) * rx,  1.0 + s]
        ])
        t = np.array([self.tx, self.ty, self.tz])
        return t + rot @ p

    def inverse(self, p: np.ndarray) -> np.ndarray:
        p = np.asarray(p, dtype=float)
        sign = -1.0 if self.convention == HelmertConvention.COORDINATE_FRAME else 1.0
        rx = self.rx * ARCSEC_TO_RAD * sign
        ry = self.ry * ARCSEC_TO_RAD * sign
        rz = self.rz * ARCSEC_TO_RAD * sign
        inv_scale = 1.0 / (1.0 + self.s_ppm * 1e-6)

        rot_t = np.array([
            [1.0,  rz, -ry],
            [-rz, 1.0,  rx],
            [ ry, -rx, 1.0]
        ]) * inv_scale
        t = np.array([self.tx, self.ty, self.tz])
        return rot_t @ (p - t)

def estimate_helmert7(src: np.ndarray, tgt: np.ndarray,
                      convention: HelmertConvention = HelmertConvention.POSITION_VECTOR) -> Helmert7:
    src, tgt = np.asarray(src, dtype=float), np.asarray(tgt, dtype=float)
    n = len(src)
    if n < 3:
        raise ValueError("Потрібно щонайменше 3 опорні пункти")

    A_rows = []
    L_rows = []

    for (x, y, z), (X, Y, Z) in zip(src, tgt):
        row_x = [1.0, 0.0, 0.0,  0.0 * ARCSEC_TO_RAD,  z * ARCSEC_TO_RAD, -y * ARCSEC_TO_RAD, x * 1e-6]
        row_y = [0.0, 1.0, 0.0, -z * ARCSEC_TO_RAD,  0.0 * ARCSEC_TO_RAD,  x * ARCSEC_TO_RAD, y * 1e-6]
        row_z = [0.0, 0.0, 1.0,  y * ARCSEC_TO_RAD, -x * ARCSEC_TO_RAD,  0.0 * ARCSEC_TO_RAD, z * 1e-6]

        if convention == HelmertConvention.COORDINATE_FRAME:
            row_x[3:6] = [-v for v in row_x[3:6]]
            row_y[3:6] = [-v for v in row_y[3:6]]
            row_z[3:6] = [-v for v in row_z[3:6]]

        A_rows.extend([row_x, row_y, row_z])
        L_rows.extend([X - x, Y - y, Z - z])

    A = np.array(A_rows)
    L = np.array(L_rows)

    # Розв'язання нормальних рівнянь (A^T A) x = A^T L
    sol, residuals, rank, s = np.linalg.lstsq(A, L, rcond=None)

    return Helmert7(
        tx=sol[0], ty=sol[1], tz=sol[2],
        rx=sol[3], ry=sol[4], rz=sol[5],
        s_ppm=sol[6],
        convention=convention
    )

if __name__ == "__main__":
    h = Helmert7(
        tx=-89.5, ty=-93.8, tz=-123.1,
        rx=0.0, ry=0.0, rz=-0.156,
        s_ppm=-1.2,
        convention=HelmertConvention.POSITION_VECTOR
    )
    p_src = np.array([3978280.0, -100410.0, 4968390.0])
    p_tgt = h.forward(p_src)
    p_inv = h.inverse(p_tgt)

    print(f"Пряме перетворення: {p_tgt}")
    print(f"Нев'язка зворотного: {(p_inv - p_src) * 1000} мм")
