#include <stdint.h>
#include "cmsis_gcc.h"          // __QADD, __get_APSR, APSR_Q_Msk

// скинути липкий прапорець Q (обнулити біти прапорців APSR)
static inline void clear_q_flag(void) {
    // у CMSIS немає __set_APSR — пишемо APSR прямо, ім'я APSR_nzcvq
    // дозволяє MSR писати групу N,Z,C,V,Q; 0 гасить усі, зокрема Q
    __asm volatile ("msr APSR_nzcvq, %0" : : "r" (0u) : "cc");
}

// чи Q піднятий (чи хоч раз насичували)
static inline int q_flag_set(void) {
    return (__get_APSR() & APSR_Q_Msk) != 0u;
}

// складаємо два блоки 16-бітних семплів із насиченням; кажемо, чи був кліпінг
int mix_saturating(int16_t *dst, const int16_t *a,
                   const int16_t *b, uint32_t n) {
    clear_q_flag();                                  // Q ← 0 один раз
    for (uint32_t i = 0; i < n; i++) {
        // __QADD насичує у 32-бітну межу; для суми двох int16 запасу з головою,
        // але межу підняв би саме кліпінг — а він тут не станеться на 16-бітних,
        // тож для чесного 16-бітного насичення беремо __SSAT після додавання:
        int32_t s = (int32_t)a[i] + b[i];
        dst[i] = (int16_t)__SSAT(s, 16);             // насичує + піднімає Q
    }
    return q_flag_set();                             // 1 → десь у блоці був кліпінг
}
