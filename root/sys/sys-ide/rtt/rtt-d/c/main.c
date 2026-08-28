#include "SEGGER_RTT.h"   // реалізація RTT від SEGGER (≈500 байтів у Flash)

volatile uint32_t g_ticks = 0;

void TIM2_IRQHandler(void) {
    g_ticks++;

    // форматує рядок і КЛАДЕ байти в кільце каналу 0 — і одразу повертається;
    // ядро НЕ чекає, поки це доїде на ПК — довезе зонд у фоні
    SEGGER_RTT_printf(0, "tick=%u\n", (unsigned)g_ticks);

    TIM2->SR &= ~TIM_SR_UIF;   // зняти прапорець переривання
}

int main(void) {
    SEGGER_RTT_Init();   // підготувати керівний блок із підписом у RAM
    // ... запуск таймера ...
    while (1) { }
}
