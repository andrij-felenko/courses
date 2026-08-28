#include <assert.h>
#include <stdint.h>
#include <stdbool.h>

// Повертає індекс key у відсортованому a[0..n-1], або -1, якщо немає.
int binary_search(const int32_t *a, int32_t n, int32_t key) {
    int32_t lo = 0;
    int32_t hi = n - 1;

    while (lo <= hi) {
        // ІНВАРІАНТ перед кожною ітерацією: межі в розумних рамках,
        // а якщо key є в масиві — він у вікні [lo, hi].
        assert(lo >= 0 && hi < n);

        // Середина БЕЗ переповнення суми (див. нижче, чому не (lo+hi)/2):
        int32_t mid = lo + (hi - lo) / 2;

        if (a[mid] == key) {
            return mid;                 // знайшли
        } else if (a[mid] < key) {
            lo = mid + 1;               // ціль правіше — відкидаємо ліву половину
        } else {
            hi = mid - 1;               // ціль лівіше — відкидаємо праву половину
        }
        // інваріант відновлено: викинута половина точно не містила key
    }
    // вийшли з lo > hi: вікно порожнє → key у масиві немає
    return -1;
}
