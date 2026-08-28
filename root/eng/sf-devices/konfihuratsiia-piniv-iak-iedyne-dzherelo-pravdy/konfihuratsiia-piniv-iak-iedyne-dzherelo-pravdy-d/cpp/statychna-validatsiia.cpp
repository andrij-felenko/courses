#include <cstdint>
#include <array>
#include <span>
#include <string_view>
#include <algorithm>

namespace hw {

enum class Port : uint8_t { A = 0, B, C, D, Max };

enum class Mode : uint8_t {
    Input     = 0x00,
    OutputPP  = 0x01,
    OutputOD  = 0x11,
    AfPP      = 0x02,
    AfOD      = 0x12,
    Analog    = 0x03
};

enum class Pull : uint8_t { None = 0, Up = 1, Down = 2 };
enum class Speed : uint8_t { Low = 0, Medium = 1, High = 2, VeryHigh = 3 };

enum class AltFunction : uint8_t {
    None = 0,
    Af1_Tim1_2 = 1,
    Af4_I2c1_3 = 4,
    Af5_Spi1_2 = 5,
    Af7_Uart1_2 = 7
};

struct PinConfig {
    Port             port;
    uint8_t          pin;
    Mode             mode;
    Pull             pull;
    Speed            speed;
    AltFunction      af;
    std::string_view label;

    constexpr bool is_open_drain() const noexcept {
        return (static_cast<uint8_t>(mode) >> 4) & 0x01;
    }

    constexpr uint8_t raw_mode() const noexcept {
        return static_cast<uint8_t>(mode) & 0x03;
    }
};

/* Імітація регістрів порту */
struct GpioRegisters {
    uint32_t moder{0};
    uint32_t otyper{0};
    uint32_t ospeedr{0};
    uint32_t pupdr{0};
    uint32_t afr[2]{0, 0};
};

/* Compile-time валідатор відсутності дублювання пінів */
template <size_t N>
consteval bool validate_unique_pins(const std::array<PinConfig, N>& pins) {
    for (size_t i = 0; i < N; ++i) {
        if (pins[i].pin > 15 || pins[i].port >= Port::Max) {
            return false;
        }
        for (size_t j = i + 1; j < N; ++j) {
            if (pins[i].port == pins[j].port && pins[i].pin == pins[j].pin) {
                return false; /* Колізія: один пін призначено двічі! */
            }
        }
    }
    return true;
}

/* Єдине джерело правди для плати */
constexpr std::array BoardPinoutSSOT = {
    PinConfig{ Port::A, 9,  Mode::AfPP,     Pull::None, Speed::VeryHigh, AltFunction::Af7_Uart1_2, "DEBUG_UART_TX" },
    PinConfig{ Port::A, 10, Mode::AfPP,     Pull::Up,   Speed::VeryHigh, AltFunction::Af7_Uart1_2, "DEBUG_UART_RX" },
    PinConfig{ Port::A, 5,  Mode::AfPP,     Pull::None, Speed::High,     AltFunction::Af5_Spi1_2,  "FLASH_SPI_SCK" },
    PinConfig{ Port::A, 6,  Mode::AfPP,     Pull::None, Speed::High,     AltFunction::Af5_Spi1_2,  "FLASH_SPI_MISO"},
    PinConfig{ Port::A, 7,  Mode::AfPP,     Pull::None, Speed::High,     AltFunction::Af5_Spi1_2,  "FLASH_SPI_MOSI"},
    PinConfig{ Port::B, 6,  Mode::AfOD,     Pull::Up,   Speed::High,     AltFunction::Af4_I2c1_3,  "SENSORS_I2C_SCL"},
    PinConfig{ Port::B, 7,  Mode::AfOD,     Pull::Up,   Speed::High,     AltFunction::Af4_I2c1_3,  "SENSORS_I2C_SDA"},
    PinConfig{ Port::C, 13, Mode::Input,    Pull::Up,   Speed::Low,      AltFunction::None,        "USER_BUTTON" },
    PinConfig{ Port::A, 8,  Mode::OutputPP, Pull::None, Speed::Low,      AltFunction::None,        "STATUS_LED" }
};

/* Гарантія на етапі компіляції: жоден пін не призначено двічі */
static_assert(validate_unique_pins(BoardPinoutSSOT), "Помилка конфігурації: виявлено конфлікт пінів!");

class PinManager {
public:
    explicit PinManager(std::span<GpioRegisters> ports) noexcept : ports_(ports) {}

    void apply(const PinConfig& p) noexcept {
        auto& reg = ports_[static_cast<size_t>(p.port)];
        const uint32_t pin = p.pin;

        /* MODER */
        reg.moder &= ~(0x03u << (pin * 2));
        reg.moder |= (static_cast<uint32_t>(p.raw_mode()) << (pin * 2));

        /* OTYPER */
        if (p.is_open_drain()) {
            reg.otyper |= (1u << pin);
        } else {
            reg.otyper &= ~(1u << pin);
        }

        /* OSPEEDR */
        reg.ospeedr &= ~(0x03u << (pin * 2));
        reg.ospeedr |= (static_cast<uint32_t>(p.speed) << (pin * 2));

        /* PUPDR */
        reg.pupdr &= ~(0x03u << (pin * 2));
        reg.pupdr |= (static_cast<uint32_t>(p.pull) << (pin * 2));

        /* AFR */
        if (p.mode == Mode::AfPP || p.mode == Mode::AfOD) {
            const uint32_t idx = pin >> 3;
            const uint32_t shift = (pin & 0x07) * 4;
            reg.afr[idx] &= ~(0x0Fu << shift);
            reg.afr[idx] |= (static_cast<uint32_t>(p.af) << shift);
        }
    }

    void init_all(std::span<const PinConfig> configs) noexcept {
        for (const auto& cfg : configs) {
            apply(cfg);
        }
    }

private:
    std::span<GpioRegisters> ports_;
};

} // namespace hw
