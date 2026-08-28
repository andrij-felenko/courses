#include <stdint.h>
#include <limits.h>

// беззнакове a * b: добуток вилазить ⇔ a > UINT_MAX / b  (при b != 0)
uint32_t mul_checked(uint32_t a, uint32_t b, int *overflowed) {
    if (b != 0 && a > UINT_MAX / b) {   // ділення безпечне: b != 0
        *overflowed = 1;
        return 0;                       // добуток НЕ рахуємо
    }
    *overflowed = 0;
    return a * b;                       // тут уже певно влізе
}
