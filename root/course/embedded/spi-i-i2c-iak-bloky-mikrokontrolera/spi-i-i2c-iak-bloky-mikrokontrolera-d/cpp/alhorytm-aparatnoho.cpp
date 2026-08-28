#include <cstdint>
#include <concepts>
#include <expected>

enum class BusRecoveryError : uint8_t {
    BusShortCircuitToGnd,
    HardwareFault
};

template <typename GpioDriver>
concept I2cRecoveryPinDriver = requires(GpioDriver drv, bool level, uint32_t us) {
    { drv.configure_pins_for_gpio() } -> std::same_as<void>;
    { drv.configure_pins_for_i2c()  } -> std::same_as<void>;
    { drv.set_scl(level)            } -> std::same_as<void>;
    { drv.set_sda(level)            } -> std::same_as<void>;
    { drv.set_sda_as_input()        } -> std::same_as<void>;
    { drv.set_sda_as_output()       } -> std::same_as<void>;
    { drv.read_sda()                } -> std::same_as<bool>;
    { drv.delay_microseconds(us)    } -> std::same_as<void>;
};

template <I2cRecoveryPinDriver GpioDriver>
class I2cBusRecovery {
public:
    explicit constexpr I2cBusRecovery(GpioDriver& driver) noexcept
        : gpio_(driver) {}

    [[nodiscard]] std::expected<void, BusRecoveryError> recover() noexcept {
        // RAII обгортка для гарантованого повернення пінів до режиму I2C
        struct PinRestorer {
            GpioDriver& drv;
            ~PinRestorer() { drv.configure_pins_for_i2c(); }
        } restorer{gpio_};

        gpio_.configure_pins_for_gpio();
        gpio_.set_sda_as_input();
        gpio_.set_scl(true);
        gpio_.delay_microseconds(10);

        // Якщо лінія вже вільна
        if (gpio_.read_sda()) {
            return {};
        }

        // Генеруємо до 9 тактів SCL
        bool line_released = false;
        for (int i = 0; i < 9; ++i) {
            gpio_.set_scl(false);
            gpio_.delay_microseconds(5);
            gpio_.set_scl(true);
            gpio_.delay_microseconds(5);

            if (gpio_.read_sda()) {
                line_released = true;
                break;
            }
        }

        if (!line_released) {
            return std::unexpected(BusRecoveryError::BusShortCircuitToGnd);
        }

        // Формуємо явну умову STOP: перепад SDA з 0 в 1 при SCL = 1
        gpio_.set_sda_as_output();
        gpio_.set_scl(false);
        gpio_.set_sda(false);
        gpio_.delay_microseconds(5);

        gpio_.set_scl(true);
        gpio_.delay_microseconds(5);
        gpio_.set_sda(true);
        gpio_.delay_microseconds(5);

        return {};
    }

private:
    GpioDriver& gpio_;
};
