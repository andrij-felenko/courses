// electrometer_guard.hpp — Ідіоматична C++17 версія з RAII та безпекою типів
#include <iostream>
#include <cmath>
#include <optional>
#include <system_error>

class ElectrometerGuard {
public:
    static constexpr float V_REF = 2.5f;
    static constexpr float ADC_MAX = 65535.0f;
    static constexpr float TIA_GAIN = 1.0e9f; // 1 В / нА
    static constexpr float MAX_LEAKAGE_PA = 50.0f; // 50 пА
    static constexpr float HUMIDITY_CRITICAL_RH = 70.0f;

    struct EnvData {
        float humidityRh{45.0f};
        float temperatureC{23.0f};
    };

    ElectrometerGuard() = default;

    void updateEnvironment(EnvData env) noexcept {
        envData_ = env;
        humidityWarning_ = (envData_.humidityRh >= HUMIDITY_CRITICAL_RH);
    }

    // Калібрування нуля: повертає оффсет або std::nullopt у разі дефекту плати
    [[nodiscard]] std::optional<float> calibrateZero(uint16_t rawAdc) noexcept {
        const float voltage = static_cast<float>(rawAdc) * (V_REF / ADC_MAX);
        const float measuredCurrentPa = (voltage / TIA_GAIN) * 1.0e12f;

        if (std::abs(measuredCurrentPa) > MAX_LEAKAGE_PA) {
            guardAlarm_ = true;
            return std::nullopt; // Похибка витоку перевищує допустимий поріг
        }

        offsetCurrentPa_ = measuredCurrentPa;
        guardAlarm_ = false;
        return offsetCurrentPa_;
    }

    [[nodiscard]] float readCurrentPa(uint16_t rawAdc) const noexcept {
        const float voltage = static_cast<float>(rawAdc) * (V_REF / ADC_MAX);
        const float rawCurrentPa = (voltage / TIA_GAIN) * 1.0e12f;
        return rawCurrentPa - offsetCurrentPa_;
    }

    [[nodiscard]] bool hasGuardAlarm() const noexcept { return guardAlarm_; }
    [[nodiscard]] bool hasHumidityWarning() const noexcept { return humidityWarning_; }

private:
    float offsetCurrentPa_{0.0f};
    EnvData envData_{};
    bool guardAlarm_{false};
    bool humidityWarning_{false};
};
