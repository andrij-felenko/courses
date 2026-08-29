// Захист від циклічного перезавантаження: після кількох падінь поспіль пристрій
// має лишитися доступним для відладчика й оновлення, а не перезапускатися вічно.
#ifndef CRASH_GUARD_H
#define CRASH_GUARD_H

#include <stdint.h>

typedef enum {
    BOOT_NORMAL = 0,  // звичайний старт: піднімаємо периферію й задачі
    BOOT_SAFE = 1     // аварійний режим: приводи вимкнені, чекаємо оновлення
} boot_mode_t;

boot_mode_t crash_guard_decide(void);

// Лічильник гаситься лише після ТРИВАЛОЇ нормальної роботи: інакше пристрій,
// який падає раз на десять хвилин, ніколи не перейде поріг.
void crash_guard_mark_healthy(uint32_t uptime_ms);

// Не повертається: або чекає команди по UART, або стрибає в системний
// завантажувач, або перезапускає чип.
__attribute__((noreturn)) void crash_guard_safe_mode(void);

#endif // CRASH_GUARD_H
