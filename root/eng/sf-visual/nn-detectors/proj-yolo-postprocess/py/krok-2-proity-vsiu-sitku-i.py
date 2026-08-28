# повертає список рамок; не більше MAX_DET
def collect(out, conf_thr):
    dets = []
    for cy in range(S):
        for cx in range(S):
            for a in range(B):
                d = decode(out, cx, cy, a)
                if d.score < conf_thr:
                    continue                  # слабка — геть одразу
                if len(dets) < MAX_DET:
                    dets.append(d)            # стеля — захист від переповнення
    return dets
