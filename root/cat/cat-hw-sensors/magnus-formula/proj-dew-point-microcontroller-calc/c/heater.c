#include "heater.h"

void heater_init(HeaterState* heater, float hysteresis, float margin) {
    heater->is_on = false;
    heater->hysteresis_c = hysteresis;
    heater->safety_margin_c = margin;
}

void heater_update(HeaterState* heater, float current_temp, float dew_point) {
    float target_min = dew_point + heater->safety_margin_c;
    float target_max = target_min + heater->hysteresis_c;

    if (current_temp <= target_min) {
        heater->is_on = true;
    } else if (current_temp >= target_max) {
        heater->is_on = false;
    }
    // В іншому випадку (в межах гістерезису) стан не змінюється
}
