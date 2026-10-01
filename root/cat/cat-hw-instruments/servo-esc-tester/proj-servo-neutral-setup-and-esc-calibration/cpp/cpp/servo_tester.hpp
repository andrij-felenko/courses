#pragma once

#include <cstdint>
#include <algorithm>

namespace hw {

/**
 * @brief Режими роботи сервотестера.
 */
enum class Mode : uint8_t {
    Manual = 0,  ///< Ручне керування зчитуванням потенціометра (1000–2000 мкс)
    Neutral,     ///< Фіксована нейтраль (1500 мкс)
    AutoSweep    ///< Автоматичне плавне хитання валу (1000–2000 мкс)
};

/**
 * @brief Стан калібрування регулятора ходу (ESC).
 */
enum class EscCalibState : uint8_t {
    Idle = 0,      ///< Калібрування не виконується
    HighThrottle,  ///< Подача 100% газу (2000 мкс)
    LowThrottle,   ///< Подача 0% газу (1000 мкс)
    Completed      ///< Завершено успішно
};

/**
 * @brief Клас ідіоматичного C++ сервотестера для мікроконтролера.
 */
class ServoTester {
public:
    static constexpr uint16_t MinPulseUs = 1000;
    static constexpr uint16_t MaxPulseUs = 2000;
    static constexpr uint16_t NeutralPulseUs = 1500;
    static constexpr uint16_t PwmPeriodUs = 20000; // 50 Гц
    static constexpr uint16_t AdcMax = 4095;
    static constexpr uint16_t SweepStepUs = 5;
    static constexpr uint32_t SweepIntervalMs = 10;
    static constexpr uint32_t DebounceMs = 50;

    ServoTester() = default;

    /**
     * @brief Ініціалізація початкового стану сервотестера.
     */
    void init();

    /**
     * @brief Перетворення значення АЦП у ширину імпульсу.
     */
    [[nodiscard]] static constexpr uint16_t mapAdcToPulse(uint16_t adcVal) noexcept {
        const uint16_t clampedAdc = std::min(adcVal, AdcMax);
        const uint32_t pulse = MinPulseUs + ((static_cast<uint32_t>(clampedAdc) * (MaxPulseUs - MinPulseUs)) / AdcMax);
        return static_cast<uint16_t>(pulse);
    }

    /**
     * @brief Задання нового режиму роботи.
     */
    void setMode(Mode newMode);

    [[nodiscard]] Mode getMode() const noexcept { return mode_; }
    [[nodiscard]] uint16_t getPulseUs() const noexcept { return pulseUs_; }
    [[nodiscard]] EscCalibState getEscCalibState() const noexcept { return escState_; }

    /**
     * @brief Оновлення ручного режиму за даними АЦП.
     */
    void updateManual(uint16_t adcVal);

    /**
     * @brief Оновлення режиму AutoSweep.
     */
    void updateSweep(uint32_t currentMs);

    /**
     * @brief Обробка антидребезгу та кліку кнопки.
     */
    void handleButton(bool rawButtonState, uint32_t currentMs);

    /**
     * @brief Старт процедури калібрування ESC.
     */
    void startEscCalibration(uint32_t currentMs);

    /**
     * @brief Оновлення автомата калібрування ESC.
     */
    void updateEscCalibration(uint32_t currentMs);

private:
    Mode mode_{Mode::Neutral};
    uint16_t pulseUs_{NeutralPulseUs};
    int8_t sweepDir_{1};
    uint32_t lastSweepMs_{0};

    bool lastBtnState_{false};
    uint32_t lastBtnDebounceMs_{0};

    EscCalibState escState_{EscCalibState::Idle};
    uint32_t escStateStartMs_{0};
};

} // namespace hw
