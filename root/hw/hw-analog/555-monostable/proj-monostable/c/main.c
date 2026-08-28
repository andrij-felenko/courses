#include <stdint.h>
#include <stdbool.h>

typedef enum { OS_IDLE, OS_ACTIVE } os_state_t;

typedef struct {
    os_state_t state;
    uint32_t   t_ms;      // тривалість імпульсу T = 1.1·R·C, у мілісекундах
    uint32_t   t_start;   // мітка часу, коли імпульс почався
} oneshot_t;

void oneshot_init(oneshot_t *os, uint32_t t_ms) {
    os->state = OS_IDLE;
    os->t_ms  = t_ms;
}

// trig — подія запуску (true рівно в момент спаду TRIG нижче ⅓V);
// now  — поточний час у мілісекундах (millis(), HAL_GetTick(), …).
// Повертає рівень виходу OUT.
bool oneshot_poll(oneshot_t *os, bool trig, uint32_t now) {
    if (os->state == OS_IDLE) {
        if (trig) {                 // подія — зводимо курок
            os->t_start = now;
            os->state   = OS_ACTIVE;
        }
    } else {                        // OS_ACTIVE: рахуємо, чи вийшов час
        // повторні запуски тут ІГНОРУЮТЬСЯ — 555 нерезапускний
        if (now - os->t_start >= os->t_ms) {
            os->state = OS_IDLE;    // імпульс добіг до кінця
        }
    }
    return os->state == OS_ACTIVE;
}
