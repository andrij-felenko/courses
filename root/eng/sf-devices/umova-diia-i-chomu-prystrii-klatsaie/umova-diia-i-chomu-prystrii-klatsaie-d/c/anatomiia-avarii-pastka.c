#include <stdbool.h>

void relay_set_power(bool enable);

void temperature_control_step(float current_temperature) {
    const float THRESHOLD = 25.0f;

    if (current_temperature < THRESHOLD) {
        relay_set_power(true);   /* Увімкнути нагрів */
    } else {
        relay_set_power(false);  /* Вимкнути нагрів */
    }
}
