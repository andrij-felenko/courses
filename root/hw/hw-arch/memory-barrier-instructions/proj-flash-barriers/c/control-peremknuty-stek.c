#include <stdint.h>

static inline void isb(void) { __asm volatile ("isb 0xF" ::: "memory"); }

// Перемкнутися на непривілейований режим (біт 0 CONTROL = 1).
void drop_privilege(void)
{
    uint32_t ctrl;
    __asm volatile ("mrs %0, control" : "=r"(ctrl));  // прочитати
    ctrl |= 1u;                                        // біт 0 = nPRIV
    __asm volatile ("msr control, %0" :: "r"(ctrl));   // записати

    isb();  // ОБОВ'ЯЗКОВО: щоб наступні команди виконувались уже за новим CONTROL
}
