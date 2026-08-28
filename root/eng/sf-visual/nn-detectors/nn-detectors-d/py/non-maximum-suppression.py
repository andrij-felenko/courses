from typing import NamedTuple

class Det(NamedTuple):
    x1: float; y1: float; x2: float; y2: float
    score: float
    cls: int

def iou_det(a: Det, b: Det) -> float:
    ix1, iy1 = max(a.x1, b.x1), max(a.y1, b.y1)
    ix2, iy2 = min(a.x2, b.x2), min(a.y2, b.y2)
    iw, ih = ix2 - ix1, iy2 - iy1
    if iw <= 0 or ih <= 0:
        return 0.0
    inter = iw * ih
    uni = (a.x2-a.x1)*(a.y2-a.y1) + (b.x2-b.x1)*(b.y2-b.y1) - inter
    return inter / uni

def nms(dets, iou_thr):
    dets = sorted(dets, key=lambda d: d.score, reverse=True)  # за спаданням упевненості
    keep = [True] * len(dets)
    for i in range(len(dets)):
        if not keep[i]:                          # вже придушена сильнішою
            continue
        for j in range(i + 1, len(dets)):
            if not keep[j]:
                continue
            if dets[j].cls != dets[i].cls:       # різні класи не конкурують
                continue
            if iou_det(dets[i], dets[j]) > iou_thr:   # двійник — геть
                keep[j] = False
    return [d for d, k in zip(dets, keep) if k]  # лишені рамки
