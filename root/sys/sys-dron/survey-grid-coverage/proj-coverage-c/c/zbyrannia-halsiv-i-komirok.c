int coverage_segments(const Pt *world, int n, double ang, double d,
                      double minlen, Seg *segs, int cap)
{
    Pt P[MAX_V];
    double xs[MAX_CUT], a0[MAX_CUT / 2], a1[MAX_CUT / 2];
    double c, s, lo, hi, H, step, y;
    int i, j, m, cnt, kept, ns = 0, base = 0, freecell = 0, prev = -1;

    if (n < 3 || n > MAX_V || d <= 0.0) return -1;

    /* 1. У систему галсів: поворот на −ang робить січні горизонтальними. */
    c = cos(ang); s = sin(ang);
    for (i = 0; i < n; i++) P[i] = rot(world[i], c, -s);

    lo = hi = P[0].y;
    for (i = 1; i < n; i++) {
        if (P[i].y < lo) lo = P[i].y;
        if (P[i].y > hi) hi = P[i].y;
    }
    H = hi - lo;

    /* 2. Скільки смуг завширшки d накриють висоту H. Мінус EPS — щоб при H,
          кратній d, шум останнього знака не додав зайвої порожньої смуги. */
    m = (int)ceil(H / d - EPS);
    if (m < 1) m = 1;
    step = H / m;          /* трохи менше за d: лінії лягають по центрах смуг */

    for (i = 0; i < m; i++) {
        y = clear_of_vertices(lo + (i + 0.5) * step, P, n);
        cnt = cuts_at(P, n, y, xs, MAX_CUT);
        if (cnt < 0) return -1;
        isort(xs, cnt);

        /* 3. Правило парності: усередині фігури лежать проміжки через один. */
        kept = 0;
        for (j = 0; j + 1 < cnt; j += 2)
            if (xs[j + 1] - xs[j] >= minlen) {
                a0[kept] = xs[j]; a1[kept] = xs[j + 1]; kept++;
            }

        /* Поки кількість шматків не міняється, j-й шматок кожної лінії — це
           та сама комірка. Зміна кількості означає критичну вершину: там
           комірки закінчуються й починаються нові. */
        if (kept != prev) { base = freecell; freecell += kept; prev = kept; }

        for (j = 0; j < kept; j++) {
            if (ns >= cap) return -1;
            segs[ns].y = y;  segs[ns].x0 = a0[j];  segs[ns].x1 = a1[j];
            segs[ns].cell = base + j;
            ns++;
        }
    }
    return ns;
}
