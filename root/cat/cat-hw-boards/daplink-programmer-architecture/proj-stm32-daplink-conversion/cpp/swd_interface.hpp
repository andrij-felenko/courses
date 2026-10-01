#ifndef SWD_INTERFACE_HPP
#define SWD_INTERFACE_HPP

#include <cstdint>
#include <string_view>
#include <iostream>

namespace daplink {

/**
 * @brief Режим роботи фізичних ліній SWD (GPIO)
 */
enum class PinMode : uint8_t {
    HighZ,          ///< Високоімпедансний стан (High-Z) — захист від фантомного живлення
    OutputPushPull, ///< Активний вихід Push-Pull (SWCLK, SWDIO при записі)
    InputFloating   ///< Вхід без підтяжки (SWDIO при зчитуванні)
};

/**
 * @brief Перетворення режиму пінів у текстове представлення
 */
constexpr std::string_view pinModeToString(PinMode mode) noexcept {
    switch (mode) {
        case PinMode::HighZ:          return "High-Z (Високий імпеданс)";
        case PinMode::OutputPushPull: return "Output Push-Pull (Активний вихід)";
        case PinMode::InputFloating:   return "Input Floating (Вхід)";
    }
    return "Невідомий режим";
}

/**
 * @brief Низькорівневе керування сигнальними лініями SWCLK та SWDIO.
 * Забезпечує двонаправлене перемикання та переведення в стан High-Z.
 */
class SwdInterface {
public:
    SwdInterface() = default;

    /**
     * @brief Ініціалізація шини SWD (за замовчуванням лінії в High-Z)
     */
    void initialize() {
        setHighZ();
    }

    /**
     * @brief Негайне переведення ліній SWCLK та SWDIO у стан High-Z.
     * Запобігає протіканню фантомного струму через захисні діоди цільового MCU.
     */
    void setHighZ() {
        m_swclkMode = PinMode::HighZ;
        m_swdioMode = PinMode::HighZ;
        m_swclkState = false;
        m_swdioState = false;
        std::cout << "  [SWD Hardware] Лінії SWCLK та SWDIO переведено у High-Z.\n";
    }

    /**
     * @brief Налаштування режиму роботи лінії SWCLK
     */
    void setSwclkMode(PinMode mode) {
        m_swclkMode = mode;
        std::cout << "  [SWD Hardware] SWCLK режим -> " << pinModeToString(mode) << "\n";
    }

    /**
     * @brief Налаштування режиму роботи лінії SWDIO
     */
    void setSwdioMode(PinMode mode) {
        m_swdioMode = mode;
        std::cout << "  [SWD Hardware] SWDIO режим -> " << pinModeToString(mode) << "\n";
    }

    /**
     * @brief Встановлення логічного рівня на лінії SWCLK
     */
    void writeSwclk(bool level) {
        if (m_swclkMode == PinMode::OutputPushPull) {
            m_swclkState = level;
        }
    }

    /**
     * @brief Встановлення логічного рівня на лінії SWDIO
     */
    void writeSwdio(bool level) {
        if (m_swdioMode == PinMode::OutputPushPull) {
            m_swdioState = level;
        }
    }

    /**
     * @brief Зчитування логічного рівня з лінії SWDIO
     */
    [[nodiscard]] bool readSwdio() const {
        return m_swdioState;
    }

    /**
     * @brief Передача 32-бітного слова через інтерфейс SWD біт-бенгінгом
     * @param data Дані для відправки
     */
    void writeWord(uint32_t data) {
        if (isHighZ()) {
            std::cout << "  [SWD Hardware] Спроба запису при активному High-Z! Запис заблоковано.\n";
            return;
        }
        setSwdioMode(PinMode::OutputPushPull);
        for (int i = 0; i < 32; ++i) {
            bool bit = (data >> i) & 1U;
            writeSwclk(false);
            writeSwdio(bit);
            writeSwclk(true);
        }
        writeSwclk(false);
    }

    /**
     * @brief Прийом 32-бітного слова через інтерфейс SWD біт-бенгінгом
     * @return Зчитане 32-бітне значення
     */
    [[nodiscard]] uint32_t readWord() {
        if (isHighZ()) {
            std::cout << "  [SWD Hardware] Спроба читання при активному High-Z! Читання заблоковано.\n";
            return 0;
        }
        setSwdioMode(PinMode::InputFloating);
        uint32_t result = 0;
        for (int i = 0; i < 32; ++i) {
            writeSwclk(false);
            writeSwclk(true);
            bool bit = readSwdio();
            result |= (static_cast<uint32_t>(bit) << i);
        }
        writeSwclk(false);
        return result;
    }

    /**
     * @brief Перевірка чи перебувають лінії у безпечному стані High-Z
     */
    [[nodiscard]] bool isHighZ() const noexcept {
        return m_swclkMode == PinMode::HighZ && m_swdioMode == PinMode::HighZ;
    }

    [[nodiscard]] PinMode getSwclkMode() const noexcept { return m_swclkMode; }
    [[nodiscard]] PinMode getSwdioMode() const noexcept { return m_swdioMode; }

private:
    PinMode m_swclkMode{PinMode::HighZ};
    PinMode m_swdioMode{PinMode::HighZ};
    bool m_swclkState{false};
    bool m_swdioState{false};
};

/**
 * @brief Клас моніторингу живлення цільової плати та автоматичного захисту від фантомного живлення.
 * Відстежує V_TARGET та сигналізує SwdInterface про необхідність переведення в High-Z.
 */
class PowerGuard {
public:
    explicit PowerGuard(SwdInterface& swd) : m_swd(swd) {}

    /**
     * @brief Перевірка стану живлення цільового мікроконтролера
     * @param targetVoltageMeasured Виміряна напруга V_TARGET у вольтах
     * @return true, якщо живлення цільової плати в нормі
     */
    bool updateTargetVoltage(float targetVoltageMeasured) {
        m_targetVoltage = targetVoltageMeasured;
        if (m_targetVoltage < MIN_SAFE_VOLTAGE_V) {
            if (!m_swd.isHighZ()) {
                std::cout << "  [PowerGuard] УВАГА: Втрата живлення цільового MCU (V_TARGET = "
                          << m_targetVoltage << " В)! Негайний перехід SWD в High-Z.\n";
                m_swd.setHighZ();
            }
            m_isTargetPowered = false;
            return false;
        }
        m_isTargetPowered = true;
        return true;
    }

    [[nodiscard]] bool isTargetPowered() const noexcept { return m_isTargetPowered; }
    [[nodiscard]] float getTargetVoltage() const noexcept { return m_targetVoltage; }

    static constexpr float MIN_SAFE_VOLTAGE_V = 1.8f;

private:
    SwdInterface& m_swd;
    float m_targetVoltage{0.0f};
    bool m_isTargetPowered{false};
};

} // namespace daplink

#endif // SWD_INTERFACE_HPP
