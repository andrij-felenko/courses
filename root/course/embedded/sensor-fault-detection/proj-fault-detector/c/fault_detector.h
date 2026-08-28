// fault_detector.h — детектор відмови одного давача-каналу.
// Голе залізо: без malloc, фіксований розмір, без блокувань.
#ifndef FAULT_DETECTOR_H
#define FAULT_DETECTOR_H

#include <stdint.h>
#include <stdbool.h>

// Який саме почерк відмови зловили (для діагностики й логів).
typedef enum {
    FD_OK = 0,        // канал здоровий
    FD_NAN,           // прийшов NaN або нескінченність
    FD_RANGE,         // виліт за фізичну межу [min..max]
    FD_RATE,          // нереальний стрибок за один крок
    FD_STALE,         // давач мовчить довше за тайм-аут
    FD_STUCK          // значення прилипло (рух менший за власний шум)
} fd_reason_t;

// Стан довіри до каналу.
typedef enum {
    FD_TRUST = 0,     // числу віримо
    FD_FAULT          // канал відкинуто, чекаємо на одужання
} fd_state_t;

// Незмінна конфігурація каналу — заповнюється раз під конкретний давач.
typedef struct {
    float    min, max;        // фізичні межі величини
    float    max_step;        // найбільша правдоподібна зміна за крок
    uint32_t timeout_ms;      // мовчання довше за це — відмова
    float    eps;             // рух менший за це вважаємо «нерухомістю»
    uint16_t stuck_limit;     // скільки нерухомих відліків поспіль — це завмер
    uint16_t trip_count;      // скільки поганих поспіль → FAULT (мале)
    uint16_t heal_count;      // скільки добрих поспіль → TRUST (велике)
} fd_config_t;

// Робочий стан каналу — нуль на старті означає «холодний, нерозігрітий».
typedef struct {
    const fd_config_t *cfg;   // вказівник на конфіг (у ПЗП/const — не копіюємо)
    fd_state_t  state;        // TRUST / FAULT
    fd_reason_t reason;       // причина останнього «погано»
    bool        primed;       // чи вже є з чим порівнювати (був ≥1 валідний)
    float       last;         // останнє ПРИЙНЯТЕ значення (для швидкості)
    uint32_t    last_ms;      // коли воно прийшло (для тайм-ауту)
    float       ref;          // опора для детектора завмеру
    uint16_t    still;        // нерухомих відліків поспіль
    uint16_t    bad_run;      // поганих відліків поспіль (рахуємо до TRIP)
    uint16_t    good_run;     // добрих відліків поспіль (рахуємо до HEAL)
} fd_channel_t;

// API.
void        fd_init(fd_channel_t *ch, const fd_config_t *cfg);  // або скидання
fd_state_t  fd_update(fd_channel_t *ch, float x, uint32_t now_ms); // 1 відлік
bool        fd_is_valid(const fd_channel_t *ch);   // зручний прапорець TRUST?
fd_reason_t fd_reason(const fd_channel_t *ch);     // чому впав (для логів)

#endif
