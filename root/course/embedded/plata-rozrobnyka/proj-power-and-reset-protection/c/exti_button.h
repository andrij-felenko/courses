/* Другий підхід: перериванням ловимо ПЕРШИЙ фронт, маскуємо лінію на час
   брязкоту й перечитуємо ніжку після одноразового таймера. У спокої кнопка не
   коштує процесору жодного такту. */
#ifndef EXTI_BUTTON_H
#define EXTI_BUTTON_H

#include "debounce.h"  /* спільний тип події button_event_t */

void exti_button_init(void);

/* Забирає накопичену подію (і одразу її гасить). Викликається з головного циклу. */
button_event_t exti_button_take_event(void);

#endif /* EXTI_BUTTON_H */
