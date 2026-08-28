// ПОГАШЕНО: поріг — одна константа. Усі знавці питають її, копій нема.
#define BATTERY_FULL_V   4.15f    // єдине джерело правди
#define BATTERY_EMPTY_V  3.30f    // заразом і нижня межа шкали

void charge_indicator(float v) {
    if (v >= BATTERY_FULL_V) led_set(LED_FULL, ON);
}

bool battery_protection(float v) {
    if (v >= BATTERY_FULL_V) { charger_disable(); return true; }
    return false;
}

void battery_log(float v) {
    if (v >= BATTERY_FULL_V) log_event(EVT_BATTERY_FULL);
}

uint8_t battery_percent(float v) {
    if (v >= BATTERY_FULL_V) return 100;
    if (v <= BATTERY_EMPTY_V) return 0;
    return (uint8_t)((v - BATTERY_EMPTY_V)
                     / (BATTERY_FULL_V - BATTERY_EMPTY_V) * 100.0f);
}

float calib_correction(float v) {
    if (v >= BATTERY_FULL_V) return CAL_HIGH;
    return CAL_LOW;
}
