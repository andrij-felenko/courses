// Виявити «застряглий» вихід ОП (ознака перевороту/защіпки) і скинути вузол.
// Якщо АЦП довго стоїть у крайньому коді — фізичний сигнал так не поводиться.
#include <stdint.h>
#include <stdbool.h>

#define ADC_MAX        4095u     // 12-бітний АЦП
#define RAIL_GUARD     20u       // «крайня» зона: ≤20 або ≥4075
#define STUCK_LIMIT    50u       // стільки поспіль вибірок у рейці = підозра

static uint16_t stuck_count = 0;

void power_cycle_analog(void);   // зняти/подати живлення аналогового вузла

bool opamp_latched(uint16_t adc) {
    bool at_rail = (adc <= RAIL_GUARD) || (adc >= ADC_MAX - RAIL_GUARD);
    stuck_count = at_rail ? (stuck_count + 1) : 0;

    if (stuck_count >= STUCK_LIMIT) {
        power_cycle_analog();    // струсонути тракт — вибити защіпку
        stuck_count = 0;
        return true;             // повідомити верхньому рівню: був збій
    }
    return false;
}
