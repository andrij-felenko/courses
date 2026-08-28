// Ідіоматичний валідатор карти пінів на сучасному C++20.
// Використовує constexpr структури, std::span, enum class та типізовані перевірки.
#include <cstdint>
#include <string_view>
#include <span>
#include <array>
#include <optional>
#include <format>
#include <expected>

enum class Port : uint8_t { A, B, C, D, None = 255 };

enum class PinFunction : uint8_t {
    GpioInput,
    GpioOutput,
    Analog,
    ExtiInterrupt,
    TimerPwm,
    Spi,
    I2c,
    Uart
};

struct PinAssignment {
    Port             port{Port::None};
    uint8_t          pin_index{0};     // 0 .. 15
    PinFunction      function{PinFunction::GpioInput};
    uint8_t          timer_id{0};      // 1 .. 8
    uint32_t         pwm_frequency{0}; // Частота у Гц
    std::string_view net_name{};
};

struct PinoutError {
    std::string message;
};

class PinoutValidator {
public:
    static constexpr size_t kExtiLines = 16;
    static constexpr size_t kMaxTimers = 8;

    [[nodiscard]] static std::expected<void, PinoutError> validate(std::span<const PinAssignment> pinout) noexcept {
        std::array<std::optional<Port>, kExtiLines> exti_allocation{};
        std::array<uint32_t, kMaxTimers + 1> timer_frequencies{};

        for (const auto& pin : pinout) {
            if (pin.port == Port::None) continue;

            // 1. Валідація ліній переривань EXTI
            if (pin.function == PinFunction::ExtiInterrupt) {
                if (pin.pin_index >= kExtiLines) {
                    return std::unexpected(PinoutError{
                        std::format("Пін {} поза межами ліній EXTI (0..15) для сигналу '{}'",
                                    pin.pin_index, pin.net_name)
                    });
                }
                const auto existing = exti_allocation[pin.pin_index];
                if (existing.has_value() && *existing != pin.port) {
                    return std::unexpected(PinoutError{
                        std::format("Колізія EXTI{}: сигнал '{}' на порті {} блокує порт {}",
                                    pin.pin_index, pin.net_name,
                                    static_cast<char>('A' + static_cast<uint8_t>(pin.port)),
                                    static_cast<char>('A' + static_cast<uint8_t>(*existing)))
                    });
                }
                exti_allocation[pin.pin_index] = pin.port;
            }

            // 2. Валідація частот таймерів ШІМ
            if (pin.function == PinFunction::TimerPwm) {
                if (pin.timer_id == 0 || pin.timer_id > kMaxTimers) {
                    return std::unexpected(PinoutError{
                        std::format("Некоректний ID таймера TIM{} для сигналу '{}'",
                                    pin.timer_id, pin.net_name)
                    });
                }
                auto& current_freq = timer_frequencies[pin.timer_id];
                if (current_freq == 0) {
                    current_freq = pin.pwm_frequency;
                } else if (current_freq != pin.pwm_frequency) {
                    return std::unexpected(PinoutError{
                        std::format("Конфлікт частоти TIM{}: сигнал '{}' вимагає {} Гц, а таймер налаштовано на {} Гц",
                                    pin.timer_id, pin.net_name, pin.pwm_frequency, current_freq)
                    });
                }
            }
        }

        return {};
    }
};
