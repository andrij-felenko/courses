#ifndef MCU_PERIPHERALS_HPP_INCLUDED
#define MCU_PERIPHERALS_HPP_INCLUDED

#include <cstdint>
#include <utility>

namespace sys {

struct PhaseCurrents {
    float iA{0.0f};
    float iB{0.0f};
    float iC{0.0f};
};

struct PeripheralsConfig {
    uint32_t pwmFrequencyHz{20000};
    uint16_t deadTimeNs{1000};
    float    shuntResistorOhm{0.010f};
    float    opampGain{16.0f};
    float    adcVref{3.3f};
};

// Клас керування апаратною периферією STM32G431
class McuPeripherals {
public:
    McuPeripherals() noexcept = default;
    ~McuPeripherals() noexcept = default;

    McuPeripherals(const McuPeripherals&) = delete;
    McuPeripherals& operator=(const McuPeripherals&) = delete;

    McuPeripherals(McuPeripherals&&) noexcept = default;
    McuPeripherals& operator=(McuPeripherals&&) noexcept = default;

    // Ініціалізація периферійних модулів TIM1, OPAMP, ADC, CORDIC
    [[nodiscard]] bool init(const PeripheralsConfig& config) noexcept;

    // Дозвіл генерації силого ШІМ
    void enablePwm(bool enable) noexcept;

    // Установка коефіцієнтів заповнення ШІМ
    void setDutyCycles(uint16_t dutyA, uint16_t dutyB, uint16_t dutyC) noexcept;

    // Зчитування фазних струмів із перетворювача АЦП
    [[nodiscard]] PhaseCurrents readPhaseCurrents() const noexcept;

    // Отримання значення періоду лічильника ШІМ
    [[nodiscard]] uint16_t getPwmPeriod() const noexcept { return pwmPeriodArr_; }

    // Апаратне обчислення косинуса та синуса через CORDIC
    [[nodiscard]] std::pair<float, float> computeCosSinCordic(float angleRad) const noexcept;

    // Калібрування зсувів вимірювальних каналів
    void calibrateOffsets() noexcept;

private:
    void initHardwareCordic() noexcept;

    uint16_t pwmPeriodArr_{0};
    float    currentScaleFactor_{1.0f};
    uint16_t rawOffsetA_{2048};
    uint16_t rawOffsetB_{2048};
    bool     isInitialized_{false};
};

} // namespace sys

#endif // MCU_PERIPHERALS_HPP_INCLUDED
