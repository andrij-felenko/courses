#include <stdint.h>

#define N_PINGS   5           // непарне — щоб медіана була одним елементом

// Медіана масиву (проста вставка; для N=5 це дешевше за будь-яку хитрість).
static uint32_t median_us(uint32_t *a, int n) {
    for (int i = 1; i < n; i++) {          // сортування вставкою
        uint32_t key = a[i];
        int j = i - 1;
        while (j >= 0 && a[j] > key) { a[j + 1] = a[j]; j--; }
        a[j + 1] = key;
    }
    return a[n / 2];                        // серединний елемент
}
