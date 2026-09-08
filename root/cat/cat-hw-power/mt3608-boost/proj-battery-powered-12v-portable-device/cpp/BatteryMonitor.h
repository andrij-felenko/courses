#pragma once

#include <cstdint>
#include <functional>
#include <string_view>

/**
 * @brief Стани заряду акумулятора 18650
 */
enum class BatteryState {
    Nominal,        // Нормальний робочий стан (> 3.4 В)
    LowWarning,     // Попередження про низький заряд (3.0–3.4 В)
    CriticalCutoff  // Критичний розряд (< 3.0 В): перетворювач вимкнено
};

/**
 * @brief Клас моніторингу напруги та захисту літій-іонного елемента живлення
 */
class BatteryMonitor {
public:
    BatteryMonitor(uint8_t enPin, uint8_t adcPin,
                   float rTopOhms = 100000.0f, float rBottomOhms = 20000.0f,
                   float vrefVolts = 1.1f, float adcMaxTicks = 1023.0f,
                   float cutoffVolts = 3.0f, float recoveryVolts = 3.3f,
                   float emaAlpha = 0.25f);

    void begin();
    void update(uint16_t rawAdc);

    [[nodiscard]] float getVoltage() const noexcept { return m_filteredVoltage; }
    [[nodiscard]] bool isBoostActive() const noexcept { return m_boostActive; }
    [[nodiscard]] BatteryState getState() const noexcept { return m_state; }

    void onStateChange(std::function<void(BatteryState, float)> callback) {
        m_callback = std::move(callback);
    }

private:
    void applyHardwareEn(bool active);
    void setState(BatteryState newState);

    uint8_t m_enPin;
    uint8_t m_adcPin;
    float m_dividerRatio;
    float m_vref;
    float m_adcMax;
    float m_cutoffVolts;
    float m_recoveryVolts;
    float m_emaAlpha;

    float m_filteredVoltage{4.0f};
    bool m_boostActive{true};
    BatteryState m_state{BatteryState::Nominal};

    std::function<void(BatteryState, float)> m_callback{nullptr};
};
