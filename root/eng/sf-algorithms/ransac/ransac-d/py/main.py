import random

def line_through(p, q):
    # пряма ax + by + c = 0 через дві точки, нормована (a² + b² = 1)
    a, b = q[1] - p[1], p[0] - q[0]
    c = -(a * p[0] + b * p[1])
    n = (a * a + b * b) ** 0.5
    return a / n, b / n, c / n

def ransac_line(pts, t, k):
    best_model, best_inliers = None, []
    for _ in range(k):
        p, q = random.sample(pts, 2)               # 1. мінімальна вибірка — 2 точки
        if p == q:
            continue
        a, b, c = line_through(p, q)               # 2. модель рівно по вибірці
        inliers = [pt for pt in pts                # 3. згода: хто ближче за t
                   if abs(a * pt[0] + b * pt[1] + c) <= t]
        if len(inliers) > len(best_inliers):       # 4. новий рекорд згоди
            best_model, best_inliers = (a, b, c), inliers
    return best_model, best_inliers                # уточнити по best_inliers — окремо
