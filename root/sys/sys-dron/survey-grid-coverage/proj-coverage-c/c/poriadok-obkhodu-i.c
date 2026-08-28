int coverage_route(const Seg *segs, int nseg, double ang, double d, double R,
                   double ext, Pt *out, int cap, double *worst_turn)
{
    int order[MAX_SEG], idx[MAX_SEG];
    int i, r, t, k, cl, last, cnt, ncell = 0, no = 0, np = 0;
    double c, s, cur = 0.0, worst = 1e30;

    if (nseg <= 0 || nseg > MAX_SEG || d <= 0.0) return -1;

    /* 4. Пропуск: розворот діаметром k·d має вмістити коло радіуса R. */
    k = (int)ceil(2.0 * R / d - EPS);
    if (k < 1) k = 1;

    for (i = 0; i < nseg; i++)
        if (segs[i].cell >= ncell) ncell = segs[i].cell + 1;

    for (cl = 0; cl < ncell; cl++) {
        cnt = 0;
        for (i = 0; i < nseg; i++)              /* уже за зростанням y */
            if (segs[i].cell == cl) idx[cnt++] = i;
        /* Пасаж r бере лінії r, r+k, r+2k…; напрямок пасажів чергується. */
        for (r = 0; r < k && r < cnt; r++) {
            if (r % 2 == 0) {
                for (i = r; i < cnt; i += k) order[no++] = idx[i];
            } else {
                last = r;
                while (last + k < cnt) last += k;
                for (i = last; i >= 0; i -= k) order[no++] = idx[i];
            }
        }
    }

    /* Найвужчий розворот усередині комірки. Якщо в жодній комірці немає двох
       ліній, лишається 1e30: розвертатися тут просто ніде. */
    for (t = 1; t < no; t++) {
        const Seg *a = &segs[order[t - 1]], *b = &segs[order[t]];
        double gap = fabs(b->y - a->y);
        if (a->cell == b->cell && gap < worst) worst = gap;
    }
    if (worst_turn) *worst_turn = worst;

    /* 5. Кінці подовжуємо, точки повертаємо назад у місцеву систему. */
    c = cos(ang); s = sin(ang);
    for (t = 0; t < no; t++) {
        const Seg *g = &segs[order[t]];
        Pt A, B, tmp;
        A.x = g->x0 - ext;  A.y = g->y;
        B.x = g->x1 + ext;  B.y = g->y;
        /* Обидва кінці на одній лінії, тож ближчий — той, чий x ближчий. */
        if (t > 0 && fabs(B.x - cur) < fabs(A.x - cur)) { tmp = A; A = B; B = tmp; }
        if (np + 2 > cap) return -1;
        out[np++] = rot(A, c, s);
        out[np++] = rot(B, c, s);
        cur = B.x;
    }
    return np;
}
