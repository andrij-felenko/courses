typedef struct { float x, y; } Pt;

// Відстань точки p до прямої (a,b) — для Рамера–Дугласа–Пекера.
static float perp_dist(Pt p, Pt a, Pt b) {
    float dx = b.x - a.x, dy = b.y - a.y;
    float len = dx * dx + dy * dy;
    if (len < 1e-6f) { dx = p.x - a.x; dy = p.y - a.y; return dx*dx + dy*dy; }
    float t = ((p.x - a.x) * dx + (p.y - a.y) * dy) / len;   // проєкція на відрізок
    float projx = a.x + t * dx, projy = a.y + t * dy;
    dx = p.x - projx; dy = p.y - projy;
    return dx * dx + dy * dy;                                // квадрат відстані
}

// Спростити замкнений контур pts[n] до чотирикутника quad[4].
// Повертає 1, якщо вийшло рівно 4 «сильні» вершини (кандидат у мітки).
static int approx_quad(const Pt *pts, int n, float eps2, Pt quad[4]) {
    if (n < 4) return 0;
    // 1) Дві найвіддаленіші точки — старт діагоналі (грубий, надійний засів).
    int i0 = 0, i1 = 0; float best = -1;
    for (int i = 1; i < n; i++) {
        float dx = pts[i].x - pts[0].x, dy = pts[i].y - pts[0].y;
        float d = dx*dx + dy*dy;
        if (d > best) { best = d; i1 = i; }
    }
    best = -1;
    for (int i = 0; i < n; i++) {
        float dx = pts[i].x - pts[i1].x, dy = pts[i].y - pts[i1].y;
        float d = dx*dx + dy*dy;
        if (d > best) { best = d; i0 = i; }
    }
    // 2) На кожній із двох дуг між i0 та i1 шукаємо найвіддаленішу точку —
    //    це ще дві вершини. Разом чотири кути квадрата.
    int lo = i0 < i1 ? i0 : i1, hi = i0 < i1 ? i1 : i0;
    int c1 = -1, c2 = -1; float b1 = eps2, b2 = eps2;
    for (int i = lo + 1; i < hi; i++) {
        float d = perp_dist(pts[i], pts[lo], pts[hi]);
        if (d > b1) { b1 = d; c1 = i; }
    }
    for (int k = 0; k < n - (hi - lo) - 1; k++) {
        int i = (hi + 1 + k) % n;
        float d = perp_dist(pts[i], pts[hi], pts[lo]);
        if (d > b2) { b2 = d; c2 = i; }
    }
    if (c1 < 0 || c2 < 0) return 0;         // не набралося 4 сильних кутів → не квадрат
    quad[0] = pts[lo]; quad[1] = pts[c1];
    quad[2] = pts[hi]; quad[3] = pts[c2];
    return 1;
}
