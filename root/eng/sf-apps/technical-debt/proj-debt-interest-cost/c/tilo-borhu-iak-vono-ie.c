#include <stdint.h>
#include <stdbool.h>

// БОРГ: гранична напруга живе п'ятьма незалежними копіями.
// Хто, дивлячись на будь-яку одну з них, знає, що інших рівно чотири?

void charge_indicator(float v) {
    if (v >= 4.20f) led_set(LED_FULL, ON);        // копія 1: індикатор
}

bool battery_protection(float v) {
    if (v >= 4.20f) { charger_disable(); return true; }  // копія 2: захист
    return false;
}

void battery_log(float v) {
    if (v >= 4.20f) log_event(EVT_BATTERY_FULL);  // копія 3: лог
}

uint8_t battery_percent(float v) {
    // лінійна шкала від 3.30 В (0%) до 4.20 В (100%)
    if (v >= 4.20f) return 100;                    // копія 4: телеметрія
    if (v <= 3.30f) return 0;
    return (uint8_t)((v - 3.30f) / (4.20f - 3.30f) * 100.0f);  // копія 4-біс!
}

float calib_correction(float v) {
    // ближче до стелі — інша поправка АЦП
    if (v >= 4.20f) return CAL_HIGH;               // копія 5: калібрування
    return CAL_LOW;
}
