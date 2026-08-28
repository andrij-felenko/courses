// ============================================================================
// proj-pinout-allocator: Сучасний типізований валідатор карти пінів на C++20.
// Використовує std::span, std::expected, constexpr перевірки та форматування.
// ============================================================================

#include <cstdint>
#include <string_view>
#include <string>
#include <vector>
#include <span>
#include <array>
#include <optional>
#include <format>
#include <expected>
#include <cmath>

enum class Port : uint8_t {
    A = 0, B, C, D, E, F, G, H, Invalid = 255
};

enum class PinType : uint8_t {
    Unused = 0,
    GpioInput,
    GpioOutput,
    ExtiInterrupt,
    AnalogInput,
    TimerPwm,
    Spi,
    I2c,
    Uart,
    HighSpeedBus
};

struct DmaRequest {
    uint8_t controller{1}; // 1 або 2
    uint8_t stream{0};     // 0 .. 7
    uint8_t channel{0};    // 0 .. 7
};

struct PinDescriptor {
    Port                    port{Port::Invalid};
    uint8_t                 pin_index{0};       // 0 .. 15
    uint16_t                package_pin_num{0}; // Фізичний номер виводу
    PinType                 type{PinType::Unused};
    uint8_t                 af_code{0};         // 0 .. 15

    uint8_t                 timer_id{0};        // 1 .. 16
    uint32_t                pwm_frequency_hz{0};

    std::optional<DmaRequest> dma{};
    std::string_view        signal_name{};
};

struct Issue {
    enum class Severity { Warning, Error };
    Severity    severity{Severity::Error};
    std::string message;
};

class PinoutValidator {
public:
    static constexpr size_t kMaxPorts = 8;
    static constexpr size_t kMaxPinsPerPort = 16;
    static constexpr size_t kExtiLines = 16;
    static constexpr size_t kMaxTimers = 16;
    static constexpr size_t kDmaControllers = 2;
    static constexpr size_t kDmaStreams = 8;

    [[nodiscard]] static std::expected<std::vector<Issue>, std::string>
    validate(std::span<const PinDescriptor> pinout) noexcept {
        std::vector<Issue> issues;

        std::array<std::optional<Port>, kExtiLines> exti_owners{};
        std::array<uint32_t, kMaxTimers + 1> timer_frequencies{};
        std::array<std::array<std::optional<size_t>, kDmaStreams>, kDmaControllers> dma_stream_owners{};
        std::array<std::array<bool, kMaxPinsPerPort>, kMaxPorts> pad_allocated{};

        for (size_t i = 0; i < pinout.size(); ++i) {
            const auto& p = pinout[i];

            if (p.port == Port::Invalid || static_cast<size_t>(p.port) >= kMaxPorts || p.pin_index >= kMaxPinsPerPort) {
                issues.push_back(Issue{
                    Issue::Severity::Error,
                    std::format("Некоректний порт або індекс піна для сигналу '{}'", p.signal_name)
                });
                continue;
            }

            const auto port_idx = static_cast<size_t>(p.port);

            // 1. Перевірка колізій фізичного паду
            if (pad_allocated[port_idx][p.pin_index]) {
                issues.push_back(Issue{
                    Issue::Severity::Error,
                    std::format("Фізичний пін P{}{{}} призначено двічі (сигнал '{}')",
                                static_cast<char>('A' + port_idx), p.pin_index, p.signal_name)
                });
            }
            pad_allocated[port_idx][p.pin_index] = true;

            // 2. Перевірка ліній переривань EXTI
            if (p.type == PinType::ExtiInterrupt) {
                const auto line = p.pin_index;
                if (exti_owners[line].has_value() && *exti_owners[line] != p.port) {
                    issues.push_back(Issue{
                        Issue::Severity::Error,
                        std::format("Колізія EXTI{}: сигнал '{}' (порт P{}) блокує лінію порту P{}",
                                    line, p.signal_name,
                                    static_cast<char>('A' + port_idx),
                                    static_cast<char>('A' + static_cast<size_t>(*exti_owners[line])))
                    });
                }
                exti_owners[line] = p.port;
            }

            // 3. Перевірка частотної узгодженості таймерів
            if (p.type == PinType::TimerPwm) {
                if (p.timer_id == 0 || p.timer_id > kMaxTimers) {
                    issues.push_back(Issue{
                        Issue::Severity::Error,
                        std::format("Некоректний ID таймера TIM{} для сигналу '{}'", p.timer_id, p.signal_name)
                    });
                } else {
                    auto& current_freq = timer_frequencies[p.timer_id];
                    if (current_freq == 0) {
                        current_freq = p.pwm_frequency_hz;
                    } else if (current_freq != p.pwm_frequency_hz) {
                        issues.push_back(Issue{
                            Issue::Severity::Error,
                            std::format("Конфлікт частоти TIM{}: сигнал '{}' вимагає {} Гц, але таймер вже налаштовано на {} Гц",
                                        p.timer_id, p.signal_name, p.pwm_frequency_hz, current_freq)
                        });
                    }
                }
            }

            // 4. Перевірка колізій потоків DMA
            if (p.dma.has_value()) {
                const auto& dma = *p.dma;
                if (dma.controller < 1 || dma.controller > kDmaControllers || dma.stream >= kDmaStreams) {
                    issues.push_back(Issue{
                        Issue::Severity::Error,
                        std::format("Некоректні параметри DMA{}_Stream{} для сигналу '{}'",
                                    dma.controller, dma.stream, p.signal_name)
                    });
                } else {
                    const auto c_idx = dma.controller - 1;
                    const auto s_idx = dma.stream;
                    if (dma_stream_owners[c_idx][s_idx].has_value() && *dma_stream_owners[c_idx][s_idx] != i) {
                        const auto& other = pinout[*dma_stream_owners[c_idx][s_idx]];
                        issues.push_back(Issue{
                            Issue::Severity::Error,
                            std::format("Колізія DMA{}_Stream{}: одночасний запит від '{}' та '{}'",
                                        dma.controller, dma.stream, p.signal_name, other.signal_name)
                        });
                    }
                    dma_stream_owners[c_idx][s_idx] = i;
                }
            }
        }

        // 5. Топологічна перевірка суміжних виводів (Analog vs High-Speed Noise)
        for (size_t i = 0; i < pinout.size(); ++i) {
            for (size_t j = i + 1; j < pinout.size(); ++j) {
                const auto& p1 = pinout[i];
                const auto& p2 = pinout[j];

                if (p1.package_pin_num == 0 || p2.package_pin_num == 0) continue;

                if (std::abs(static_cast<int>(p1.package_pin_num) - static_cast<int>(p2.package_pin_num)) == 1) {
                    const bool p1_noisy = (p1.type == PinType::HighSpeedBus || p1.type == PinType::Spi);
                    const bool p2_analog = (p2.type == PinType::AnalogInput);

                    const bool p2_noisy = (p2.type == PinType::HighSpeedBus || p2.type == PinType::Spi);
                    const bool p1_analog = (p1.type == PinType::AnalogInput);

                    if ((p1_noisy && p2_analog) || (p2_noisy && p1_analog)) {
                        issues.push_back(Issue{
                            Issue::Severity::Warning,
                            std::format("Топологічний ризик завад: швидкісний цифровий сигнал '{}' (вивід {}) "
                                        "розташований поруч із чутливим аналоговим входом '{}' (вивід {})",
                                        p1_noisy ? p1.signal_name : p2.signal_name,
                                        p1_noisy ? p1.package_pin_num : p2.package_pin_num,
                                        p1_analog ? p1.signal_name : p2.signal_name,
                                        p1_analog ? p1.package_pin_num : p2.package_pin_num)
                        });
                    }
                }
            }
        }

        return issues;
    }
};
