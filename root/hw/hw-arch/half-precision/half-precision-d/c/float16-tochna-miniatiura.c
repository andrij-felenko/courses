#include <stdio.h>

int main(void) {
    _Float16 big = 70000.0f16;    // більше за стелю 65504
    _Float16 tiny = 1e-8f16;      // менше за найменше денормальне

    printf("%f\n", (float)big);   // inf   ← переповнення до нескінченності
    printf("%f\n", (float)tiny);  // 0.000000  ← зникло до нуля
    return 0;
}
