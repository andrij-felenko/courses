import numpy as np

# pts[N,2] — точки, cent[K,2] — центри, assign[N] — попереднє присвоєння
# повертає нове присвоєння і скільки точок змінили групу (0 => можна спинятись)
def assign_step(pts, cent, assign):
    # квадрати відстаней кожної точки до кожного центру; корінь зайвий — порядок той самий
    d2 = np.sum((pts[:, None, :] - cent[None, :, :]) ** 2, axis=2)
    best = np.argmin(d2, axis=1)       # найближчий центр для кожної точки
    changed = int(np.sum(best != assign))
    return best, changed
