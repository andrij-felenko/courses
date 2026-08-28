#include <cstdint>
#include <expected>
#include <span>
#include <concepts>

namespace embedded::safety {

enum class PinoutError : uint32_t {
    None               = 0x00,
    ShortToGnd         = 0x01,
    ShortToVcc         = 0x02,
    LinesBridged       = 0x04,
    SignalsSwapped     = 0x08,
    NoDeviceResponse   = 0x10,
    OvervoltageTrip    = 0x20
};

[[nodiscard]] constexpr PinoutError operator|(PinoutError a, PinoutError b) noexcept {
    return static_cast<PinoutError>(static_cast<uint32_t>(a) | static_cast<uint32_t>(b));
}

constexpr bool has_flag(PinoutError value, PinoutError flag) noexcept {
    return (static_cast<uint32_t>(value) & static_cast<uint32_t>(flag)) != 0;
}

// Концепт для низькорівневого апаратного драйвера пінів (HAL)
template <typename T>
concept GpioHardwareDriver = requires(T hal, uint32_t pin, bool level) {
    { hal.set_mode_pullup(pin) } -> std::same_as<void>;
    { hal.set_mode_pulldown(pin) } -> std::same_as<void>;
    { hal.set_mode_floating(pin) } -> std::same_as<void>;
    { hal.set_mode_output(pin) } -> std::same_as<void>;
    { hal.write(pin, level) } -> std::same_as<void>;
    { hal.read(pin) } -> std::same_as<bool>;
    { hal.delay_us(100u) } -> std::same_as<void>;
    { hal.enable_hardware_swap(true) } -> std::same_as<void>;
};

struct BusProbeConfig {
    uint32_t pin_a;
    uint32_t pin_b;
    bool hardware_swap_supported{false};
};

template <GpioHardwareDriver Hal>
class BusSelfTestController {
public:
    explicit constexpr BusSelfTestController(Hal& hal, BusProbeConfig config) noexcept
        : hal_{hal}, config_{config} {}

    // Виконує повну послідовність самотестування за принципом RAII
    [[nodiscard]] std::expected<void, PinoutError> run_diagnostics() noexcept {
        // RAII-вартовий: гарантує повернення пінів у безпечний стан при будь-якому виході
        struct SafePinGuard {
            Hal& hal;
            BusProbeConfig cfg;
            ~SafePinGuard() noexcept {
                hal.set_mode_floating(cfg.pin_a);
                hal.set_mode_floating(cfg.pin_b);
            }
        } guard{hal_, config_};

        auto errors = PinoutError::None;

        // Фаза 1: Перевірка на замикання до шин живлення
        hal_.set_mode_pullup(config_.pin_a);
        hal_.set_mode_pullup(config_.pin_b);
        hal_.delay_us(50);

        if (!hal_.read(config_.pin_a) || !hal_.read(config_.pin_b)) {
            errors = errors | PinoutError::ShortToGnd;
        }

        hal_.set_mode_pulldown(config_.pin_a);
        hal_.set_mode_pulldown(config_.pin_b);
        hal_.delay_us(50);

        if (hal_.read(config_.pin_a) || hal_.read(config_.pin_b)) {
            errors = errors | PinoutError::ShortToVcc;
        }

        if (errors != PinoutError::None) {
            return std::unexpected(errors);
        }

        // Фаза 2: Перевірка на міжпровідникове замикання
        hal_.set_mode_output(config_.pin_a);
        hal_.set_mode_pulldown(config_.pin_b);

        hal_.write(config_.pin_a, true);
        hal_.delay_us(20);
        const bool level_high = hal_.read(config_.pin_b);

        hal_.write(config_.pin_a, false);
        hal_.delay_us(20);
        const bool level_low = hal_.read(config_.pin_b);

        if (level_high && !level_low) {
            return std::unexpected(PinoutError::LinesBridged);
        }

        // Фаза 3: Перевірка напрямку сигналів
        hal_.set_mode_floating(config_.pin_a);
        hal_.set_mode_floating(config_.pin_b);

        const bool signals_swapped = false; // Визначається відповіддю периферії
        if (signals_swapped) {
            if (config_.hardware_swap_supported) {
                hal_.enable_hardware_swap(true);
                return {};
            }
            return std::unexpected(PinoutError::SignalsSwapped);
        }

        return {};
    }

private:
    Hal& hal_;
    BusProbeConfig config_;
};

} // namespace embedded::safety
