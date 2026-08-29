/* Міст «USART1 → фонове завдання» за шаблоном Top-Half / Bottom-Half. */
#ifndef UART_ISR_H
#define UART_ISR_H

#include <stdint.h>

/* Що верхня половина встигла помітити. Пише лише ISR, читає лише фон,
 * тому 32-бітні вирівняні лічильники безпечні без критичної секції:
 * на Cortex-M одиничні LDR/STR неподільні. */
typedef struct {
    volatile uint32_t bytes_received;
    volatile uint32_t ring_overflows; /* кільце не встигли вичитати */
    volatile uint32_t hw_overruns;    /* апаратний ORE: байт загублено в залізі */
    volatile uint32_t worst_cycles;   /* найдовший прохід ISR, такти ядра */
} uart_isr_stats_t;

/* Запускає нижню половину. Завдання створюється СТАТИЧНО: купи в цьому
 * проєкті немає взагалі, і це не аскеза, а наслідок правила «жодного
 * malloc на шляху переривання». */
void uart_bridge_start(void);

const uart_isr_stats_t *uart_bridge_stats(void);

#endif /* UART_ISR_H */
