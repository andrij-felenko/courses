#include <stdint.h>
#include <stdbool.h>

typedef struct {
    fs_state_t state;          // де ми зараз
    uint32_t   last_change_ms; // коли востаннє міняли стан (для журналу/діагностики)
    bool       beacon;         // чи горить маяк
} failsafe_t;

// Пороги переходів — у ПРОПУЩЕНИХ ударах, не в мілісекундах.
// hb_period_ms — оцінений період серцебиття (його дає детектор присутності).
#define BEATS_TO_HOLD   3u   // 3 удари тиші поспіль → HOLD
#define BEATS_TO_STOP  10u   // 10 ударів → SAFE-STOP
#define BEATS_TO_RTL   50u   // 50 ударів → політика місії
