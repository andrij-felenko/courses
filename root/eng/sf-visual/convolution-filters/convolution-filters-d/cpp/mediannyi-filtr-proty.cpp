#include <stdint.h>
static inline void swap_u8(uint8_t *a, uint8_t *b){
    if (*a > *b){ uint8_t t = *a; *a = *b; *b = t; }
}
/* медіана дев'яти: відсортувати достатньо, щоб 5-й елемент став на місце */
static uint8_t median9(uint8_t v[9]){
    /* мережа сортування для 9 елементів дає median у v[4] */
    for (int i = 0; i < 5; ++i)            /* частковий вибірковий прохід */
        for (int j = i + 1; j < 9; ++j)
            swap_u8(&v[i], &v[j]);         /* після i=4 v[4] = 5-й за порядком */
    return v[4];
}
static inline int clampi(int x, int lo, int hi){
    return x < lo ? lo : (x > hi ? hi : x);
}
void median3(const uint8_t *src, uint8_t *dst, int w, int h){
    for (int y = 0; y < h; ++y)
        for (int x = 0; x < w; ++x){
            uint8_t v[9]; int k = 0;
            for (int dy = -1; dy <= 1; ++dy)          /* зібрати окіл 3x3 */
                for (int dx = -1; dx <= 1; ++dx){
                    int yi = clampi(y+dy, 0, h-1);
                    int xi = clampi(x+dx, 0, w-1);
                    v[k++] = src[(size_t)yi*w + xi];
                }
            dst[(size_t)y*w + x] = median9(v);
        }
}
