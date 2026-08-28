#include <cstdint>

namespace embedded::naive {

// Наївна реакція на сирий вхід без фільтрації
void ProcessConveyorSensorNaive(bool raw_pin_level, uint32_t &item_counter) noexcept {
    static bool prev_level = false;

    // Реакція на кожен перепад 0 -> 1
    if (raw_pin_level && !prev_level) {
        ++item_counter;
    }
    prev_level = raw_pin_level;
}

} // namespace embedded::naive
