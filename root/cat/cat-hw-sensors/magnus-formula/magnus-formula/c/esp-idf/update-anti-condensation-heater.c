#include <stdbool.h>

// Алгоритм гістерезисного керування протиконденсатним нагрівачем
bool update_anti_condensation_heater(float temp_surface, float dew_point, bool current_heater_state) {
    const float margin_on = 3.0f;  // Поріг увімкнення (+3 °C вище точки роси)
    const float margin_off = 6.0f; // Поріг вимкнення (+6 °C вище точки роси)

    float threshold_on = dew_point + margin_on;
    float threshold_off = dew_point + margin_off;

    if (temp_surface <= threshold_on) {
        return true;  // Активація нагріву
    } else if (temp_surface >= threshold_off) {
        return false; // Деактивація нагріву
    }

    return current_heater_state; // Збереження поточного стану (зона гістерезису)
}
