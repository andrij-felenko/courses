def iou(a, b):
    ix1, iy1 = max(a.x1, b.x1), max(a.y1, b.y1)
    ix2, iy2 = min(a.x2, b.x2), min(a.y2, b.y2)
    iw, ih = ix2 - ix1, iy2 - iy1
    if iw <= 0.0 or ih <= 0.0:
        return 0.0                                    # не торкаються
    inter = iw * ih
    uni = (a.x2-a.x1)*(a.y2-a.y1) + (b.x2-b.x1)*(b.y2-b.y1) - inter
    return inter / uni

# NMS на місці: лишені позначає keep[i]=True; повертає їх кількість.
def nms(d, iou_thr, keep):
    n = len(d)
    # сортування за спаданням оцінки (n мала після фільтра — бульбашки досить)
    d.sort(key=lambda x: x.score, reverse=True)
    for i in range(n):
        keep[i] = True
    for i in range(n):
        if not keep[i]:
            continue                                  # вже придушена
        for j in range(i + 1, n):                     # лише слабші за i
            if not keep[j] or d[j].cls != d[i].cls:
                continue                              # різні класи не конкурують
            if iou(d[i], d[j]) > iou_thr:
                keep[j] = False                       # двійник — геть
    return sum(keep)
