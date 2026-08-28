# Точку зберігаємо як кортеж (x, y).

# Квадрат відстані точки p до прямої (a,b) — для Рамера–Дугласа–Пекера.
def perp_dist(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = dx * dx + dy * dy
    if length < 1e-6:                                   # a==b: відстань до точки
        dx, dy = p[0] - a[0], p[1] - a[1]
        return dx * dx + dy * dy
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length   # проєкція на відрізок
    projx, projy = a[0] + t * dx, a[1] + t * dy
    dx, dy = p[0] - projx, p[1] - projy
    return dx * dx + dy * dy                             # квадрат відстані

# Спростити замкнений контур pts до чотирикутника.
# Повертає список із 4 вершин, якщо набралося 4 «сильні» кути; інакше None.
def approx_quad(pts, eps2):
    n = len(pts)
    if n < 4:
        return None
    # 1) Дві найвіддаленіші точки — старт діагоналі (грубий, надійний засів).
    i1 = max(range(1, n),
             key=lambda i: (pts[i][0] - pts[0][0])**2 + (pts[i][1] - pts[0][1])**2)
    i0 = max(range(n),
             key=lambda i: (pts[i][0] - pts[i1][0])**2 + (pts[i][1] - pts[i1][1])**2)
    # 2) На кожній із двох дуг між i0 та i1 шукаємо найвіддаленішу точку —
    #    це ще дві вершини. Разом чотири кути квадрата.
    lo, hi = min(i0, i1), max(i0, i1)
    c1 = c2 = None
    b1 = b2 = eps2
    for i in range(lo + 1, hi):
        d = perp_dist(pts[i], pts[lo], pts[hi])
        if d > b1:
            b1, c1 = d, i
    for k in range(n - (hi - lo) - 1):
        i = (hi + 1 + k) % n
        d = perp_dist(pts[i], pts[hi], pts[lo])
        if d > b2:
            b2, c2 = d, i
    if c1 is None or c2 is None:            # не набралося 4 сильних кутів → не квадрат
        return None
    return [pts[lo], pts[c1], pts[hi], pts[c2]]
