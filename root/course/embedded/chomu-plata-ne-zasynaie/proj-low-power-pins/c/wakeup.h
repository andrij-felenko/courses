/* Джерела пробудження: кнопка на EXTI0 і будильник RTC.
 *
 * Модуль існує окремо, бо порядок «спершу налаштувати вихід, потім засинати»
 * порушується найчастіше: плата, що заснула без жодного дозволеного джерела,
 * зовні не відрізняється від зависання.
 */
#ifndef WAKEUP_H
#define WAKEUP_H

#include "mcu.h"

typedef enum {
    WAKE_NONE = 0,
    WAKE_BUTTON,
    WAKE_RTC
} wake_reason_t;

/* Одноразове налаштування: EXTI0 на фронт кнопки, RTC на періодичний будильник. */
void wakeup_init(void);

/* Заводить будильник RTC на задану кількість секунд. */
void wakeup_arm_rtc(uint16_t seconds);

/* Скидає прапорці EXTI, RTC і черги NVIC.
 * Без цього WFI повернеться миттєво: незнятий pending будить ядро одразу. */
void wakeup_clear_pending(void);

/* Причина останнього пробудження — її записують обробники переривань. */
wake_reason_t wakeup_last_reason(void);

const char *wake_reason_str(wake_reason_t r);

#endif /* WAKEUP_H */
