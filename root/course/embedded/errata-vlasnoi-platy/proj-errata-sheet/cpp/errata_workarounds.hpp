/* errata_workarounds.hpp — Ідіоматична обгортка обхідних шляхів (C++20) */
#pragma once
#include <cstdint>
#include <concepts>
#include <span>

enum class BoardRevision : uint8_t {
    Unknown = 0,
    RevA    = 1,
    RevB    = 2
};

enum class PinMode {
    InputFloating,
    OutputPushPull,
    AlternateOpenDrain
};

enum class PinState : bool {
    Low  = false,
    High = true
};

/* Апаратний інтерфейс абстракції */
class IGpioController {
public:
    virtual ~IGpioController() = default;
    virtual void setMode(uint8_t port, uint8_t pin, PinMode mode) = 0;
    virtual void write(uint8_t port, uint8_t pin, PinState state) = 0;
    virtual PinState read(uint8_t port, uint8_t pin) = 0;
    virtual void delayMs(uint32_t ms) = 0;
    virtual bool initI2c() = 0;
    virtual void deinitI2c() = 0;
};

/* =========================================================================
 * 1. RAII-керування живленням давача з обходом ERR-HW-001
 * ========================================================================= */
class SensorPowerManager {
public:
    SensorPowerManager(IGpioController& gpio, BoardRevision rev)
        : m_gpio(gpio), m_rev(rev) {}

    [[nodiscard]] bool safePowerCycle() noexcept {
        if (m_rev == BoardRevision::RevA) {
            // КРОК 1: Деініціалізація периферії I2C
            m_gpio.deinitI2c();

            // КРОК 2: Ізоляція сигнальних ліній (High-Z)
            m_gpio.setMode(kPortI2c, kPinSda, PinMode::InputFloating);
            m_gpio.setMode(kPortI2c, kPinScl, PinMode::InputFloating);

            // КРОК 3: Знеструмлення VDD
            m_gpio.setMode(kPortPwr, kPinPwr, PinMode::OutputPushPull);
            m_gpio.write(kPortPwr, kPinPwr, PinState::Low);

            // КРОК 4: Пауза для гарантованого розряджання ємностей
            m_gpio.delayMs(30);

            // КРОК 5: Подача VDD
            m_gpio.write(kPortPwr, kPinPwr, PinState::High);
            m_gpio.delayMs(15);

            // КРОК 6: Відновлення конфігурації шини I2C
            m_gpio.setMode(kPortI2c, kPinSda, PinMode::AlternateOpenDrain);
            m_gpio.setMode(kPortI2c, kPinScl, PinMode::AlternateOpenDrain);

            return m_gpio.initI2c();
        } else {
            // У Rev B використовується нативне апаратне скидання
            m_gpio.write(kPortPwr, kPinPwr, PinState::Low);
            m_gpio.delayMs(2);
            m_gpio.write(kPortPwr, kPinPwr, PinState::High);
            m_gpio.delayMs(5);
            return true;
        }
    }

private:
    static constexpr uint8_t kPortPwr = 0;
    static constexpr uint8_t kPinPwr  = 4;
    static constexpr uint8_t kPortI2c = 1;
    static constexpr uint8_t kPinSda  = 7;
    static constexpr uint8_t kPinScl  = 6;

    IGpioController& m_gpio;
    BoardRevision    m_rev;
};

/* =========================================================================
 * 2. Шаблонний антидребезговий фільтр стабільного вікна (ERR-HW-003)
 * ========================================================================= */
template <size_t HistoryDepth = 8>
class SoftwareDebouncer {
    static_assert(HistoryDepth <= 32, "History depth must fit in uint32_t");

public:
    constexpr SoftwareDebouncer(uint8_t port, uint8_t pin) noexcept
        : m_port(port), m_pin(pin), m_history(kMaskAllOnes), m_stableState(true) {}

    void init(IGpioController& gpio) noexcept {
        gpio.setMode(m_port, m_pin, PinMode::InputFloating);
    }

    [[nodiscard]] bool update(IGpioController& gpio) noexcept {
        const auto raw = gpio.read(m_port, m_pin);
        const uint32_t bit = (raw == PinState::High) ? 1U : 0U;

        m_history = ((m_history << 1) | bit) & kMaskAllOnes;

        // Перевірка стабільного натискання (усі нулі)
        if (m_history == 0 && m_stableState) {
            m_stableState = false;
            return true; // Подія: натиснуто
        }

        // Перевірка стабільного відпускання (усі одиниці)
        if (m_history == kMaskAllOnes && !m_stableState) {
            m_stableState = true;
        }

        return false;
    }

    [[nodiscard]] bool isPressed() const noexcept {
        return !m_stableState;
    }

private:
    static constexpr uint32_t kMaskAllOnes = (1ULL << HistoryDepth) - 1ULL;

    uint8_t  m_port;
    uint8_t  m_pin;
    uint32_t m_history;
    bool     m_stableState;
};
