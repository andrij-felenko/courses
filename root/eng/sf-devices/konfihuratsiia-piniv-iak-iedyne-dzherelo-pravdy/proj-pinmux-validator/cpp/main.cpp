#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <array>
#include <span>
#include <cstdint>
#include <iomanip>

namespace pinmux {

enum class Port : uint8_t { A = 0, B, C, D, Max };

enum class DriverMode : uint8_t {
    Input,
    OutputPushPull,
    OutputOpenDrain,
    AlternatePushPull,
    AlternateOpenDrain,
    Analog
};

enum class PullMode : uint8_t { None, Up, Down };

enum class AltFunction : uint8_t {
    Gpio = 0,
    Af1_Timer = 1,
    Af4_I2c = 4,
    Af5_Spi = 5,
    Af7_Usart = 7
};

enum class Severity { Info, Warning, Error };

struct PinCapability {
    uint16_t supported_af_mask{1u << static_cast<uint8_t>(AltFunction::Gpio)};
    bool     supports_analog{false};
    bool     is_5v_tolerant{true};

    constexpr bool supports_af(AltFunction af) const noexcept {
        return (supported_af_mask & (1u << static_cast<uint8_t>(af))) != 0;
    }
};

struct BoardPin {
    Port             port;
    uint8_t          pin;
    DriverMode       mode;
    PullMode         pull;
    AltFunction      af;
    bool             enable_exti{false};
    std::string_view signal_name;
    std::string_view owner_module;
};

struct Diagnostic {
    Severity    severity;
    Port        port;
    uint8_t     pin;
    std::string message;
};

class PinMuxValidator {
public:
    PinMuxValidator() {
        init_mcu_capabilities();
    }

    void init_mcu_capabilities() noexcept {
        for (auto& port_caps : capabilities_) {
            for (auto& pin_cap : port_caps) {
                pin_cap.supported_af_mask = (1u << static_cast<uint8_t>(AltFunction::Gpio));
                pin_cap.supports_analog = false;
                pin_cap.is_5v_tolerant = true;
            }
        }

        /* Налаштування карти периферії */
        capabilities_[static_cast<size_t>(Port::A)][0].supports_analog = true;
        capabilities_[static_cast<size_t>(Port::A)][0].supported_af_mask |= (1u << 1);

        capabilities_[static_cast<size_t>(Port::A)][5].supported_af_mask |= (1u << 5);
        capabilities_[static_cast<size_t>(Port::A)][6].supported_af_mask |= (1u << 5);
        capabilities_[static_cast<size_t>(Port::A)][7].supported_af_mask |= (1u << 5);

        capabilities_[static_cast<size_t>(Port::A)][9].supported_af_mask  |= (1u << 7) | (1u << 1);
        capabilities_[static_cast<size_t>(Port::A)][10].supported_af_mask |= (1u << 7) | (1u << 1);

        capabilities_[static_cast<size_t>(Port::B)][6].supported_af_mask |= (1u << 4);
        capabilities_[static_cast<size_t>(Port::B)][7].supported_af_mask |= (1u << 4);
    }

    [[nodiscard]] bool validate(std::span<const BoardPin> pins) {
        diagnostics_.clear();
        errors_ = 0;
        warnings_ = 0;

        std::array<std::array<const BoardPin*, 16>, 4> allocated{};
        std::array<const BoardPin*, 16> exti_allocated{};

        for (const auto& p : pins) {
            const auto port_idx = static_cast<size_t>(p.port);
            if (port_idx >= 4 || p.pin >= 16) {
                add_diag(Severity::Error, p.port, p.pin, "Неприпустимі координати виводу!");
                continue;
            }

            /* 1. Колізія множинного володіння */
            if (allocated[port_idx][p.pin] != nullptr) {
                const auto* prev = allocated[port_idx][p.pin];
                add_diag(Severity::Error, p.port, p.pin,
                         std::string("Колізія володіння: '") + std::string(p.signal_name) +
                         "' (" + std::string(p.owner_module) + ") конфліктує з '" +
                         std::string(prev->signal_name) + "' (" + std::string(prev->owner_module) + ")");
            } else {
                allocated[port_idx][p.pin] = &p;
            }

            /* 2. Перевірка підтримки AF */
            const auto& cap = capabilities_[port_idx][p.pin];
            if (p.mode == DriverMode::AlternatePushPull || p.mode == DriverMode::AlternateOpenDrain) {
                if (!cap.supports_af(p.af)) {
                    add_diag(Severity::Error, p.port, p.pin,
                             std::string("Альтернативна функція AF") + std::to_string(static_cast<int>(p.af)) +
                             " не підтримується кремнієм для сигналу '" + std::string(p.signal_name) + "'");
                }
            }

            /* 3. Перевірка режиму відкритого стоку I2C */
            if (p.af == AltFunction::Af4_I2c && p.mode == DriverMode::AlternatePushPull) {
                add_diag(Severity::Error, p.port, p.pin,
                         "Шина I2C вимагає Open-Drain режиму! Push-Pull спричинить блокування шини");
            }

            /* 4. Перевірка аналогового режиму */
            if (p.mode == DriverMode::Analog) {
                if (!cap.supports_analog) {
                    add_diag(Severity::Error, p.port, p.pin,
                             "Вивід не підтримує аналоговий вхід перетворювача ADC");
                }
                if (p.pull != PullMode::None) {
                    add_diag(Severity::Warning, p.port, p.pin,
                             "Підтяжка в аналоговому режимі спотворює точність ADC");
                }
            }

            /* 5. Плаваючий цифровий вхід */
            if (p.mode == DriverMode::Input && p.pull == PullMode::None) {
                add_diag(Severity::Warning, p.port, p.pin,
                         "Плаваючий вхід (Floating Input) генерує струми витоку в CMOS інверторі");
            }

            /* 6. Колізія переривань EXTI */
            if (p.enable_exti) {
                if (exti_allocated[p.pin] != nullptr) {
                    const auto* prev_exti = exti_allocated[p.pin];
                    add_diag(Severity::Error, p.port, p.pin,
                             std::string("Конфлікт каналу EXTI") + std::to_string(p.pin) +
                             ": спільний вектор із P" + static_cast<char>('A' + static_cast<int>(prev_exti->port)) +
                             std::to_string(prev_exti->pin) + " ('" + std::string(prev_exti->signal_name) + "')");
                } else {
                    exti_allocated[p.pin] = &p;
                }
            }
        }

        return errors_ == 0;
    }

    void print_report() const {
        std::cout << "====================================================\n";
        std::cout << "        ЗВІТ ВАЛІДАЦІЇ КОНФІГУРАЦІЇ ПІНІВ (C++20)   \n";
        std::cout << "====================================================\n";

        for (const auto& d : diagnostics_) {
            std::string_view tag = (d.severity == Severity::Error)   ? "[ПОМИЛКА] " :
                                   (d.severity == Severity::Warning) ? "[ЗАСТЕРЕЖЕННЯ] " : "[ІНФО]   ";
            std::cout << tag << "P" << static_cast<char>('A' + static_cast<int>(d.port))
                      << std::setw(2) << std::setfill('0') << static_cast<int>(d.pin)
                      << ": " << d.message << "\n";
        }

        std::cout << "----------------------------------------------------\n";
        std::cout << "Підсумок: " << errors_ << " помилок, " << warnings_ << " застережень.\n";
        if (errors_ == 0) {
            std::cout << "СТАТУС: [УСПІХ] Конфігурація плати верифікована.\n";
        } else {
            std::cout << "СТАТУС: [ВІДХИЛЕНО] Знайдено критичні колізії!\n";
        }
        std::cout << "====================================================\n";
    }

    [[nodiscard]] size_t error_count() const noexcept { return errors_; }
    [[nodiscard]] size_t warning_count() const noexcept { return warnings_; }

private:
    void add_diag(Severity sev, Port port, uint8_t pin, std::string msg) {
        diagnostics_.push_back(Diagnostic{sev, port, pin, std::move(msg)});
        if (sev == Severity::Error) errors_++;
        if (sev == Severity::Warning) warnings_++;
    }

    std::array<std::array<PinCapability, 16>, 4> capabilities_{};
    std::vector<Diagnostic> diagnostics_;
    size_t errors_{0};
    size_t warnings_{0};
};

} // namespace pinmux

int main() {
    using namespace pinmux;

    PinMuxValidator validator;

    constexpr std::array board_manifest = {
        BoardPin{ Port::A, 9,  DriverMode::AlternatePushPull, PullMode::None, AltFunction::Af7_Usart, false, "DEBUG_UART_TX",  "uart_driver" },
        BoardPin{ Port::A, 10, DriverMode::AlternatePushPull, PullMode::Up,   AltFunction::Af7_Usart, false, "DEBUG_UART_RX",  "uart_driver" },
        BoardPin{ Port::A, 9,  DriverMode::OutputPushPull,    PullMode::None, AltFunction::Gpio,      false, "STATUS_LED",     "led_driver" },
        BoardPin{ Port::A, 9,  DriverMode::AlternatePushPull, PullMode::None, AltFunction::Af5_Spi,   false, "FLASH_SPI_MOSI", "spi_driver" },
        BoardPin{ Port::B, 6,  DriverMode::AlternatePushPull, PullMode::Up,   AltFunction::Af4_I2c,   false, "SENSORS_I2C_SCL", "i2c_driver" },
        BoardPin{ Port::B, 7,  DriverMode::AlternateOpenDrain,PullMode::Up,   AltFunction::Af4_I2c,   false, "SENSORS_I2C_SDA", "i2c_driver" },
        BoardPin{ Port::A, 0,  DriverMode::Input,             PullMode::Down, AltFunction::Gpio,      true,  "USER_BUTTON",    "button_drv" },
        BoardPin{ Port::B, 0,  DriverMode::Input,             PullMode::Up,   AltFunction::Gpio,      true,  "ACCEL_INT1",     "sensor_drv" },
        BoardPin{ Port::A, 0,  DriverMode::Analog,            PullMode::Up,   AltFunction::Gpio,      false, "VBAT_SENSE",     "power_mgr" }
    };

    bool is_valid = validator.validate(board_manifest);
    validator.print_report();

    return is_valid ? 0 : 1;
}
