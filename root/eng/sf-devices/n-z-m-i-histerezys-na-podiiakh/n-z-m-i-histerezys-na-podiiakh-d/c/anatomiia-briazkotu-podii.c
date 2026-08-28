#include <stdbool.h>
#include <stdint.h>

/* Наївна реакція на сирий вхід без фільтрації */
void process_conveyor_sensor_naive(bool raw_pin_level, uint32_t *item_counter) {
    static bool prev_level = false;

    /* Реакція на кожен перепад 0 -> 1 */
    if (raw_pin_level && !prev_level) {
        (*item_counter)++;
    }
    prev_level = raw_pin_level;
}
