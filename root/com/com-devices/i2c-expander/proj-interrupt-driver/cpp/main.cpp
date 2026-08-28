#include <cstdint>
#include <expected>
#include <span>
#include <concepts>

enum class ExpanderError {
    BusError,
    InvalidPin,
    Timeout
};

template <typename I2CBus>
concept I2CTransceiver = requires(I2CBus bus, uint8_t addr, uint8_t reg, std::span<const uint8_t> out_buf, std::span<uint8_t> in_buf) {
    { bus.write(addr, reg, out_buf) } -> std::same_as<bool>;
    { bus.read(addr, reg, in_buf) } -> std::same_as<bool>;
};

template <I2CTransceiver Bus>
class Mcp23017 {
public:
    enum class PinMode { Output, Input, InputPullup };

    explicit Mcp23017(Bus& bus, uint8_t address = 0x20)
        : bus_(bus), address_(address), shadow_olat_(0x0000), shadow_iodir_(0xFFFF) {}

    std::expected<void, ExpanderError> initialize() {
        constexpr uint8_t reg_iocon = 0x0A;
        constexpr uint8_t iocon_val = (1 << 6) | (1 << 2); // MIRROR | Open-Drain ODR
        const uint8_t payload[] = { iocon_val };

        if (!bus_.write(address_, reg_iocon, payload)) {
            return std::unexpected(ExpanderError::BusError);
        }
        return {};
    }

    std::expected<void, ExpanderError> setPinMode(uint8_t pin, PinMode mode) {
        if (pin >= 16) return std::unexpected(ExpanderError::InvalidPin);

        if (mode == PinMode::Output) {
            shadow_iodir_ &= ~(1 << pin);
        } else {
            shadow_iodir_ |= (1 << pin);
        }

        const uint8_t iodir_data[2] = {
            static_cast<uint8_t>(shadow_iodir_ & 0xFF),
            static_cast<uint8_t>((shadow_iodir_ >> 8) & 0xFF)
        };

        if (!bus_.write(address_, 0x00 /* IODIRA */, iodir_data)) {
            return std::unexpected(ExpanderError::BusError);
        }

        if (mode == PinMode::InputPullup) {
            const uint8_t reg = (pin < 8) ? 0x0C : 0x0D; // GPPUA / GPPUB
            uint8_t current_gppu = 0;
            uint8_t buf[1] = {0};
            if (!bus_.read(address_, reg, buf)) return std::unexpected(ExpanderError::BusError);
            buf[0] |= static_cast<uint8_t>(1 << (pin % 8));
            if (!bus_.write(address_, reg, buf)) return std::unexpected(ExpanderError::BusError);
        }
        return {};
    }

    std::expected<void, ExpanderError> writePin(uint8_t pin, bool value) {
        if (pin >= 16) return std::unexpected(ExpanderError::InvalidPin);

        if (value) {
            shadow_olat_ |= (1 << pin);
        } else {
            shadow_olat_ &= ~(1 << pin);
        }

        const uint8_t reg = (pin < 8) ? 0x14 : 0x15; // OLATA : OLATB
        const uint8_t payload[] = {
            static_cast<uint8_t>((pin < 8) ? (shadow_olat_ & 0xFF) : ((shadow_olat_ >> 8) & 0xFF))
        };

        if (!bus_.write(address_, reg, payload)) {
            return std::unexpected(ExpanderError::BusError);
        }
        return {};
    }

    struct InterruptEvent {
        uint16_t triggered_pins;
        uint16_t captured_values;
    };

    std::expected<InterruptEvent, ExpanderError> readInterruptSnapshot() {
        uint8_t intf_buf[2] = {0, 0};
        uint8_t intcap_buf[2] = {0, 0};

        if (!bus_.read(address_, 0x0E /* INTFA */, intf_buf)) {
            return std::unexpected(ExpanderError::BusError);
        }
        if (!bus_.read(address_, 0x10 /* INTCAPA */, intcap_buf)) {
            return std::unexpected(ExpanderError::BusError);
        }

        InterruptEvent evt{
            .triggered_pins = static_cast<uint16_t>(intf_buf[0] | (intf_buf[1] << 8)),
            .captured_values = static_cast<uint16_t>(intcap_buf[0] | (intcap_buf[1] << 8))
        };
        return evt;
    }

private:
    Bus& bus_;
    uint8_t address_;
    uint16_t shadow_olat_;
    uint16_t shadow_iodir_;
};
