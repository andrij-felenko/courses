def nms(dets, tau):
    dets.sort(key=lambda d: d.score, reverse=True)   # крок 2
    keep = [True] * len(dets)
    for i, di in enumerate(dets):
        if not keep[i]:                              # вже придушена — пропустити
            continue
        for j in range(i + 1, len(dets)):            # лише дальші (вони слабші)
            dj = dets[j]
            if not keep[j] or dj.cls != di.cls:
                continue
            if iou(di.box, dj.box) > tau:            # крок 4
                keep[j] = False
    return [d for d, k in zip(dets, keep) if k]      # лишені рамки
