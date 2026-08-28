#include <stdint.h>
#include <stdbool.h>

// Межа зі сценарію: перерва не довша за 30 секунд.
#define SCENARIO_MAX_OUTAGE_MS  30000u

typedef struct {
    uint32_t down_at_ms;   // коли головний вузол перестав відповідати (стимул)
    uint32_t up_at_ms;     // коли резерв почав обслуговувати (відповідь)
    bool     serving;      // чи хтось узагалі обслуговує запити
} Failover;

// true — сценарій виконано (перерва в межах міри); false — порушено.
bool failover_meets_scenario(const Failover *f)
{
    if (!f->serving)                 // взагалі не піднялися — це відмова
        return false;

    uint32_t outage = f->up_at_ms - f->down_at_ms;   // фактична перерва, мс
    return outage <= SCENARIO_MAX_OUTAGE_MS;          // порівняння з мірою
}
