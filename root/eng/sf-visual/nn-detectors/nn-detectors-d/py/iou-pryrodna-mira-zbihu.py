from typing import NamedTuple

# рамка: x1,y1 — лівий верх; x2,y2 — правий низ
class Box(NamedTuple):
    x1: float; y1: float; x2: float; y2: float

def area(b: Box) -> float:
    return (b.x2 - b.x1) * (b.y2 - b.y1)

def iou(a: Box, b: Box) -> float:
    # перетин: правіший лівий край ... лівіший правий край
    ix1 = max(a.x1, b.x1)                     # max(x1)
    iy1 = max(a.y1, b.y1)                     # max(y1)
    ix2 = min(a.x2, b.x2)                     # min(x2)
    iy2 = min(a.y2, b.y2)                     # min(y2)

    iw = ix2 - ix1                            # ширина перетину
    ih = iy2 - iy1                            # висота перетину
    if iw <= 0.0 or ih <= 0.0:               # не торкаються
        return 0.0
    inter = iw * ih

    uni = area(a) + area(b) - inter          # об'єднання без подвійного рахунку
    return inter / uni
