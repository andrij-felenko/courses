#include <stdint.h>

static inline int mirror(int i, int n) {     // дзеркалить індекс у [0, n-1]
    if (i < 0)  i = -i;                       // -1 -> 1, -2 -> 2 (просте відбиття)
    if (i >= n) i = 2*(n-1) - i;              // n -> n-2, n+1 -> n-3
    if (i < 0)  i = 0;                        // страховка для дуже малих n
    return i;
}
// безпечне читання: ніколи не вилазить за масив, по краях — дзеркало
static inline uint8_t at(int H, int W, const uint8_t raw[H][W], int y, int x) {
    return raw[mirror(y, H)][mirror(x, W)];
}
// тепер увесь алгоритм читає лише через at(...): край обробляється тим самим кодом,
// без жодного окремого "if (y==0)" — і ніде немає доступу за межі масиву.
