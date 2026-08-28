#include <stdint.h>

#define SCB_CCR (*(volatile uint32_t *)0xE000ED14)  // Configuration and Control
#define CCR_DIV_0_TRP (1u << 4)                      // біт 4: пастка на ділення на 0

void enable_div0_trap(void) {
    SCB_CCR |= CCR_DIV_0_TRP;   // тепер a / 0 підніме UsageFault, а не поверне 0
}

int safe_divide(int a, int b) {
    if (b == 0) {               // головний захист — у коді, не сподіваймось на залізо
        return 0;               // або: сигналізувати про помилку вище за викликом
    }
    return a / b;               // сюди дійдемо, лише коли ділення справді законне
}
