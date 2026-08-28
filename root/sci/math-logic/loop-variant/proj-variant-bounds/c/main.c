#include <stddef.h>

/* Здається, рахує вниз від n−1 до 0. Насправді — не спиняється ніколи. */
void walk_backwards(const int *a, size_t n)
{
    for (size_t i = n - 1; i >= 0; i--)   /* i БЕЗЗНАКОВЕ: умова тотожно істинна */
        use(a[i]);                        /* при i = 0 крок i-- дає SIZE_MAX */
}

/* Так правильно: перевірка й крок в одному, дно недосяжне знизу. */
void walk_backwards_ok(const int *a, size_t n)
{
    for (size_t i = n; i-- > 0; )
        use(a[i]);
}
