from dataclasses import dataclass

@dataclass
class Box:
    x: int; y: int; w: int; h: int; score: float

def iou(a: Box, b: Box) -> float:
    x1 = max(a.x, b.x)                       # ліва межа перетину
    y1 = max(a.y, b.y)                       # верхня
    x2 = min(a.x + a.w, b.x + b.w)           # права
    y2 = min(a.y + a.h, b.y + b.h)           # нижня
    iw, ih = x2 - x1, y2 - y1
    if iw <= 0 or ih <= 0:
        return 0.0                           # не перетинаються
    inter = iw * ih
    uni   = a.w * a.h + b.w * b.h - inter
    return inter / uni
