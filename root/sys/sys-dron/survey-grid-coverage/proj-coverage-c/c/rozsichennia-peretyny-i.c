static Pt rot(Pt p, double c, double s)
{
    Pt q;
    q.x = p.x * c - p.y * s;
    q.y = p.x * s + p.y * c;
    return q;
}

/* Перетини січної y = const із контуром. Повертає їхню кількість або −1. */
static int cuts_at(const Pt *P, int n, double y, double *xs, int cap)
{
    int i, c = 0;
    for (i = 0; i < n; i++) {
        Pt a = P[i], b = P[(i + 1) % n];
        /* Напівінтервал [a.y, b.y): нижній кінець сторони «свій», верхній — ні.
           Горизонтальна сторона (a.y == b.y) дає порожній інтервал і випадає
           сама — ділення на нуль нижче стає неможливим. */
        if (!((a.y <= y && y < b.y) || (b.y <= y && y < a.y)))
            continue;
        if (c >= cap) return -1;
        xs[c++] = a.x + (y - a.y) * (b.x - a.x) / (b.y - a.y);
    }
    return c;
}

static void isort(double *a, int n)
{
    int i, j;
    for (i = 1; i < n; i++) {
        double v = a[i];
        for (j = i - 1; j >= 0 && a[j] > v; j--)
            a[j + 1] = a[j];
        a[j + 1] = v;
    }
}
