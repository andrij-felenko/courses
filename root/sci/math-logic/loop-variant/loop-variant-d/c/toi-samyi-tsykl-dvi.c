#include <assert.h>
#include <stddef.h>

ptrdiff_t bsearch_i(const int *a, size_t n, int target) {
    size_t lo = 0, hi = n;                /* вікно [lo, hi) */
    while (lo < hi) {
        size_t v = hi - lo;               /* варіант — ширина вікна */
        size_t mid = lo + (hi - lo) / 2;  /* різниця невід'ємна: переповнитись нема з чого */
        if (a[mid] == target) return (ptrdiff_t)mid;
        if (a[mid] < target) lo = mid + 1;
        else                 hi = mid;
        assert(hi - lo < v);              /* вікно строго звузилось */
    }
    return -1;
}
