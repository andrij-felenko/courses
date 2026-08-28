#include <cstdint>
#include <concepts>
#include "sensor_driver.hpp"

namespace driver {

template <typename GpioControl>
requires requires(GpioControl gpio, bool level, uint32_t us) {
    { gpio.set_scl(level) } -> std::same_as<void>;
    { gpio.set_sda(level) } -> std::same_as<void>;
    { gpio.get_sda() } -> std::same_as<bool>;
    { gpio.delay_us(us) } -> std::same_as<void>;
    { gpio.switch_to_gpio_od() } -> std::same_as<void>;
    { gpio.switch_to_i2c_hardware() } -> std::same_as<void>;
}
class I2cBusRecovery {
public:
    explicit I2cBusRecovery(GpioControl& gpio) noexcept : m_gpio(gpio) {}

    [[nodiscard]] Status recover() noexcept {
        m_gpio.switch_to_gpio_od();
        m_gpio.set_scl(true);
        m_gpio.set_sda(true);
        m_gpio.delay_us(5);

        if (!m_gpio.get_sda()) {
            for (uint8_t i = 0; i < 9; ++i) {
                m_gpio.set_scl(false);
                m_gpio.delay_us(5);
                m_gpio.set_scl(true);
                m_gpio.delay_us(5);

                if (m_gpio.get_sda()) {
                    break;
                }
            }
        }

        if (!m_gpio.get_sda()) {
            m_gpio.switch_to_i2c_hardware();
            return Status::BusStuck;
        }

        // Генерація послідовності STOP
        m_gpio.set_sda(false);
        m_gpio.delay_us(5);
        m_gpio.set_scl(true);
        m_gpio.delay_us(5);
        m_gpio.set_sda(true);
        m_gpio.delay_us(5);

        m_gpio.switch_to_i2c_hardware();
        return Status::Ok;
    }

private:
    GpioControl& m_gpio;
};

} // namespace driver
