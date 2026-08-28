#include <stdint.h>
static inline int clampi(int v, int lo, int hi){
    return v < lo ? lo : (v > hi ? hi : v);
}
/* один піксель гаусу 3x3; сума ваг 16 → нормування = зсув на 4 з округленням */
static uint8_t gauss3_px(const uint8_t *s, int w, int h, int x, int y){
    static const int wk[3][3] = {{1,2,1},{2,4,2},{1,2,1}};
    int32_t acc = 0;
    for (int dy = -1; dy <= 1; ++dy)
        for (int dx = -1; dx <= 1; ++dx){
            int yi = clampi(y+dy, 0, h-1);
            int xi = clampi(x+dx, 0, w-1);
            acc += wk[dy+1][dx+1] * s[(size_t)yi*w + xi];
        }
    return (uint8_t)((acc + 8) >> 4);   /* +8 = пів-дільника → округлення до найближчого */
}
