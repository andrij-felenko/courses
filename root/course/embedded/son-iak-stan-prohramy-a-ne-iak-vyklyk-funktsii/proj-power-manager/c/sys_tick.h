/* sys_tick.h — системний лічильник часу з підтримкою бестікового простою. */
#ifndef SYS_TICK_H
#define SYS_TICK_H

#include <stdint.h>

void     sys_tick_init(uint32_t sysclk_hz);
uint32_t sys_tick_now_ms(void);

/* Глушить SysTick на час глибокого сну й повертає його з поправкою на
 * фактично проспаний час — саме це й називають tickless idle. */
void     sys_tick_suspend(void);
void     sys_tick_resume(uint32_t slept_ms);

/* Скільки лишилося до дедлайну; 0, якщо він уже минув.
 * Різниця рахується зі знаком, тож перехід через 2^32 нічого не ламає. */
uint32_t sys_tick_until(uint32_t deadline_ms);

#endif /* SYS_TICK_H */
