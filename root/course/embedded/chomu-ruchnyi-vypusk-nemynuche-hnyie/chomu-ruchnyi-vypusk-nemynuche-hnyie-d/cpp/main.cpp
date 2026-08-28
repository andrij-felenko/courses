/* Ідіоматичний еквівалент на C++20 */
#include <cstdint>

[[nodiscard]] bool check_hardware_ready() noexcept {
    bool status{false}; /* Явна безпечна ініціалізація */
    if (gpio_read_pin(READY_PIN)) {
        status = true;
    }
    return status;
}
