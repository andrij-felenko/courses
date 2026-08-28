#include <cstdint>

class I2cBusRecovery {
public:
    struct GpioInterface {
        void (*set_opendrain_mode)() noexcept;
        void (*set_alternate_mode)() noexcept;
        void (*set_scl)(bool level) noexcept;
        bool (*read_sda)() noexcept;
        void (*delay_us)(uint32_t us) noexcept;
    };

    explicit constexpr I2cBusRecovery(const GpioInterface& gpio) noexcept
        : gpio_(gpio) {}

    [[nodiscard]] bool recover() const noexcept {
        gpio_.set_opendrain_mode();
        gpio_.delay_us(10);

        if (gpio_.read_sda()) {
            gpio_.set_alternate_mode();
            return true;
        }

        bool recovered = false;
        for (uint8_t i = 0; i < 9; ++i) {
            gpio_.set_scl(false);
            gpio_.delay_us(5);
            gpio_.set_scl(true);
            gpio_.delay_us(5);

            if (gpio_.read_sda()) {
                recovered = true;
                break;
            }
        }

        // Формування умови STOP
        gpio_.set_scl(false);
        gpio_.delay_us(5);
        gpio_.set_scl(true);
        gpio_.delay_us(5);

        gpio_.set_alternate_mode();
        return recovered;
    }

private:
    GpioInterface gpio_;
};
