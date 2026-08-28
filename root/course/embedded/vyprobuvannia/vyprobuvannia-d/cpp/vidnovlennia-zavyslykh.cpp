// C++20 варіант: RAII-обгортка для безпечного відновлення периферії
#include <cstdint>
#include <chrono>
#include <concepts>

namespace hal {

template<typename GpioDriver>
class I2cBusRecovery {
public:
    static bool unlock_bus(GpioDriver& gpio, uint8_t scl_pin, uint8_t sda_pin) noexcept {
        gpio.set_open_drain(scl_pin);
        gpio.set_open_drain(sda_pin);

        gpio.write(sda_pin, 1);
        gpio.write(scl_pin, 1);
        gpio.delay_microseconds(5);

        if (gpio.read(sda_pin) == 1) {
            return true;
        }

        for (int i = 0; i < 9; ++i) {
            gpio.write(scl_pin, 0);
            gpio.delay_microseconds(5);
            gpio.write(scl_pin, 1);
            gpio.delay_microseconds(5);

            if (gpio.read(sda_pin) == 1) {
                break;
            }
        }

        // Ручна STOP умова
        gpio.write(sda_pin, 0);
        gpio.delay_microseconds(5);
        gpio.write(scl_pin, 1);
        gpio.delay_microseconds(5);
        gpio.write(sda_pin, 1);
        gpio.delay_microseconds(5);

        return (gpio.read(sda_pin) == 1);
    }
};

} // namespace hal
