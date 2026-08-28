#include <stdint.h>

// EMA у форматі Q (state зберігає значення × 2^SHIFT, тобто з дробовими бітами).
// α = 1/2^SHIFT.  Стан ширший за вихід — дріб не втрачається між кроками.
#define EMA_SHIFT 3            // α = 1/8

int32_t ema_fixed(int32_t x) {
    static int32_t state = 0;  // масштаб ×2^SHIFT (акумулятор із дробом)
    static int primed = 0;
    if (!primed) { state = x << EMA_SHIFT; primed = 1; }   // прайминг у масштабі стану
    // state += α·(x − state):  x підняти в масштаб стану, різницю зсунути на SHIFT
    state += ((x << EMA_SHIFT) - state) >> EMA_SHIFT;
    return state >> EMA_SHIFT;  // повернути у звичайний масштаб (з відкиданням дробу лише на ВИХОДІ)
}
