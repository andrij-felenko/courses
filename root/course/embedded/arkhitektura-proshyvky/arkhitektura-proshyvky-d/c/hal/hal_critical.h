/* hal/hal_critical.h — коротка критична секція.
 * Черга подій — єдина структура, яку одночасно чіпають переривання й
 * головний цикл, тож саме їй потрібне неподільне оновлення індексів.
 * Функція повертає попередній стан маски, щоб вкладений виклик не вмикав
 * переривання передчасно — класична пастка голого cpsie всередині ISR. */
#ifndef HAL_CRITICAL_H
#define HAL_CRITICAL_H

#include <stdint.h>

uint32_t hal_critical_enter(void);
void     hal_critical_exit(uint32_t saved_state);

#endif /* HAL_CRITICAL_H */
