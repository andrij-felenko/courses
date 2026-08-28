#include <stdint.h>

// Керівні регістри контролера переривань (Cortex-M, спрощено).
#define NVIC_ICER0  (*(volatile uint32_t *)0xE000E180u)  // вимкнути лінію
#define NVIC_ISER0  (*(volatile uint32_t *)0xE000E100u)  // увімкнути лінію

static inline void dsb(void) { __asm volatile ("dsb 0xF" ::: "memory"); }
static inline void isb(void) { __asm volatile ("isb 0xF" ::: "memory"); }

void update_shared(int irq, shared_t *s) {
    NVIC_ICER0 = (1u << irq);   // просимо вимкнути переривання…
    dsb();                      // …дочекатися, поки вимкнення справді дійшло
    isb();                      // …і далі йти вже за новим станом

    modify(s);                  // тепер обробник точно не влетить сюди

    NVIC_ISER0 = (1u << irq);   // вмикаємо назад
    dsb(); isb();               // щоб дозвіл подіяв негайно
}
