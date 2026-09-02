#ifndef STARTUP_GUARD_H
#define STARTUP_GUARD_H

/*
 * Захисний інтервал старту: єдиний код, що виконується до будь-якої
 * ініціалізації периферії. Його задача — гарантувати налагоджувачу вікно,
 * у якому ядро ще не встигло ні перепризначити PA13/PA14, ні заснути.
 */

#include <stdbool.h>
#include <stdint.h>

/* Тривалість вікна очікування (мс) та вивід кнопки аварійного утримання. */
#define GUARD_WINDOW_MS      2000U
#define GUARD_DEBOUNCE_MS      20U

typedef enum {
    GUARD_PROCEED = 0,        /* вікно минуло, можна вмикати решту прошивки */
    GUARD_HELD_BY_OPERATOR    /* кнопку затиснуто — далі йти не можна        */
} guard_result_t;

/*
 * Тримає блок налагодження живим у режимах SLEEP/STOP/STANDBY.
 * Без цього ядро, що заснуло через 50 мкс після старту, зникає з шини SWD.
 */
void startup_guard_keep_debug_in_low_power(void);

/* Чи вже сидить налагоджувач на шині (біт C_DEBUGEN у DHCSR). */
bool startup_guard_debugger_attached(void);

/* Витримує захисне вікно, стежачи за кнопкою відновлення. */
guard_result_t startup_guard_run(void);

/* Безпечний вічний цикл: ядро працює, тактування живе, DAP відповідає. */
void startup_guard_park(void);

#endif /* STARTUP_GUARD_H */
