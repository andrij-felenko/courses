import math
from typing import NamedTuple

class FlowN(NamedTuple):          # нормальний потік у точці
    u: float
    v: float
    mag: float

# градієнт і часова похідна в пікселі (x,y); нормальна складова потоку
def normal_flow(prev, curr, W, x, y):
    # центральні різниці по поточному кадру → просторовий градієнт
    Ix = 0.5 * (curr[y*W + x+1] - curr[y*W + x-1])
    Iy = 0.5 * (curr[(y+1)*W + x] - curr[(y-1)*W + x])
    # різниця між кадрами в тій самій точці → часова похідна
    It = curr[y*W + x] - prev[y*W + x]

    g2 = Ix*Ix + Iy*Iy                    # квадрат модуля градієнта
    if g2 < 1.0:
        return FlowN(0.0, 0.0, 0.0)       # немає градієнта — потік невизначений

    # в'язь Ix·u + Iy·v + It = 0 дає ЛИШЕ рух уздовж градієнта (нормальний):
    #   (u,v) = -It · (Ix,Iy) / |∇I|²
    return FlowN(
        u=-It * Ix / g2,
        v=-It * Iy / g2,
        mag=abs(It) / math.sqrt(g2),      # довжина нормальної складової
    )
