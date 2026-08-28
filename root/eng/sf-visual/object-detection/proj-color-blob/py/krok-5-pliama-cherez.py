import numpy as np

def find_blob(m, min_area):              # m: бінарна маска HxW (0/255)
    ys, xs = np.nonzero(m)               # координати всіх білих пікселів
    M00 = xs.size                        # площа: скільки білих пікселів
    if M00 < min_area:                   # замало пікселів — це шум, не ціль
        return None
    cx = int(xs.sum() // M00)            # центроїд (суми — int64, не переповнюються)
    cy = int(ys.sum() // M00)
    return {
        "cx": cx, "cy": cy, "area": int(M00),
        "x0": int(xs.min()), "y0": int(ys.min()),   # габарити
        "x1": int(xs.max()), "y1": int(ys.max()),
    }
