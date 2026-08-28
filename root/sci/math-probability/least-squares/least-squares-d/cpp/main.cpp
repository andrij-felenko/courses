/* Інкрементна лінійна регресія: y ≈ k·x + b за найменшими квадратами.
   Точки не зберігаємо — лише п'ять накопичувачів. */
typedef struct {
    uint32_t n;       /* кількість точок                 */
    double sx, sy;    /* Σx,  Σy                          */
    double sxx, sxy;  /* Σx², Σ(x·y)                      */
} fit_t;

void fit_add(fit_t *f, double x, double y)   /* згодувати один вимір */
{
    f->n  += 1u;
    f->sx += x;       f->sy  += y;
    f->sxx += x * x;  f->sxy += x * y;
}

/* Дістати пряму. Повертає 0, якщо нахил визначений, інакше −1
   (усі x однакові → знаменник нуль, прямої не провести). */
int fit_solve(const fit_t *f, double *k, double *b)
{
    double den = (double)f->n * f->sxx - f->sx * f->sx;   /* n·Σx² − (Σx)² */
    if (den == 0.0) return -1;                            /* вертикальна хмара */

    *k = ((double)f->n * f->sxy - f->sx * f->sy) / den;   /* нахил  */
    *b = (f->sy - *k * f->sx) / (double)f->n;             /* зсув   */
    return 0;
}
