/* Зсунути січну з рівня будь-якої вершини. Кроків не більше, ніж вершин:
   кожен крок віддаляє y від того рівня, на який він щойно натрапив. */
static double clear_of_vertices(double y, const Pt *P, int n)
{
    int pass, i, hit;
    for (pass = 0; pass <= n; pass++) {
        hit = 0;
        for (i = 0; i < n; i++)
            if (fabs(P[i].y - y) < Y_TOL) { hit = 1; break; }
        if (!hit) break;
        y += Y_STEP;
    }
    return y;
}
