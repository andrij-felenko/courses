/* Ідіоматичний C++ клас відновлення шини I2C через RAII пін-маніпулятор */
#include <cstdint>

namespace driver {

template <typename GpioDriver>
class I2cBusRecovery {
public:
    static bool recover(GpioDriver& gpio, uint8_t scl_pin, uint8_t sda_pin) noexcept {
        gpio.set_open_drain_output(scl_pin);
        gpio.set_input_pullup(sda_pin);

        for (int i = 0; i < 9; ++i) {
            if (gpio.read(sda_pin) == 1) {
                break;
            }
            gpio.write(scl_pin, 0);
            gpio.delay_us(5);
            gpio.write(scl_pin, 1);
            gpio.delay_us(5);
        }

        gpio.set_open_drain_output(sda_pin);
        gpio.write(sda_pin, 0);
        gpio.delay_us(5);
        gpio.write(scl_pin, 1);
        gpio.delay_us(5);
        gpio.write(sda_pin, 1);
        gpio.delay_us(5);

        return gpio.read(sda_pin) == 1;
    }
};

} // namespace driver
