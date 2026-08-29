/* Переривання TIM2 — приклад правильного квитування прапорця. */
#ifndef TIMER_ISR_H
#define TIMER_ISR_H

#include <stdint.h>

/* Мілісекундний лічильник, який веде TIM2. Вирівняне 32-бітне слово,
 * тож читання з будь-якого контексту неподільне. */
uint32_t timer_ms_ticks(void);

/* Скільки разів NVIC зайшов у TIM2_IRQHandler, не заставши там прапорця:
 * саме цей лічильник ловить помилковий повторний вхід через буфер запису. */
uint32_t timer_spurious_entries(void);

#endif /* TIMER_ISR_H */
