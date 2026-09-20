#include <cstdint>

class DipSwitchGPIOReader {
private:
    volatile std::uint32_t* gpio_in_reg;
    std::uint8_t pin_shift;
    bool active_low;

public:
    DipSwitchGPIOReader(volatile std::uint32_t* reg, std::uint8_t shift, bool active_low_flag)
        : gpio_in_reg(reg), pin_shift(shift), active_low(active_low_flag) {}

    std::uint8_t readRaw() const {
        std::uint32_t port_val = *gpio_in_reg;
        std::uint8_t raw_byte = static_cast<std::uint8_t>((port_val >> pin_shift) & 0xFF);
        return active_low ? static_cast<std::uint8_t>((~raw_byte) & 0xFF) : raw_byte;
    }
};
