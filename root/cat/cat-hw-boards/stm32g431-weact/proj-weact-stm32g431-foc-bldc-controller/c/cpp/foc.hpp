#ifndef FOC_HPP_INCLUDED
#define FOC_HPP_INCLUDED

#include "mcu_periph.hpp"
#include <tuple>
#include <algorithm>

namespace control {

// Дискретний ПІ-регулятор із анти-віндапом на C++
class PiController {
public:
    constexpr PiController() noexcept = default;
    constexpr PiController(float kp, float ki, float outMin, float outMax) noexcept
        : kp_(kp), ki_(ki), outMin_(outMin), outMax_(outMax) {}

    float update(float setpoint, float measured, float dt) noexcept {
        if (dt <= 0.0f) return 0.0f;

        const float error = setpoint - measured;
        const float pTerm = kp_ * error;

        integral_ += ki_ * error * dt;
        integral_ = std::clamp(integral_, outMin_, outMax_);

        return std::clamp(pTerm + integral_, outMin_, outMax_);
    }

    void reset() noexcept { integral_ = 0.0f; }

private:
    float kp_{0.0f};
    float ki_{0.0f};
    float integral_{0.0f};
    float outMin_{-1.0f};
    float outMax_{1.0f};
};

// Клас ядра векторного керування (FOC)
class FocController {
public:
    FocController() noexcept = default;

    void init(float busVoltage, uint16_t pwmPeriod) noexcept;

    // Перетворення координат
    [[nodiscard]] std::pair<float, float> clarkeTransform(float iA, float iB) const noexcept;
    [[nodiscard]] std::pair<float, float> parkTransform(float iAlpha, float iBeta, float cosTh, float sinTh) const noexcept;
    [[nodiscard]] std::pair<float, float> inverseParkTransform(float vD, float vQ, float cosTh, float sinTh) const noexcept;

    // Просторово-векторна модуляція (SVPWM)
    [[nodiscard]] std::tuple<uint16_t, uint16_t, uint16_t> calculateSvpwm(float vAlpha, float vBeta) const noexcept;

    // Цикли керування
    void updateCurrentLoop(float electricalAngle, float dt, sys::McuPeripherals& periph) noexcept;
    void updateSpeedLoop(float measuredSpeed, float dt) noexcept;

    void setTargetSpeed(float speedRadS) noexcept { targetSpeed_ = speedRadS; }
    void setTargetId(float idAmp) noexcept { targetId_ = idAmp; }

    [[nodiscard]] float getMeasuredSpeed() const noexcept { return measuredSpeed_; }
    [[nodiscard]] float getIq() const noexcept { return iQ_; }
    [[nodiscard]] float getId() const noexcept { return iD_; }

private:
    float busVoltage_{24.0f};
    uint16_t pwmPeriod_{4250};

    float iA_{0.0f}, iB_{0.0f}, iC_{0.0f};
    float iAlpha_{0.0f}, iBeta_{0.0f};
    float iD_{0.0f}, iQ_{0.0f};

    float targetId_{0.0f};
    float targetIq_{0.0f};
    float targetSpeed_{0.0f};
    float measuredSpeed_{0.0f};

    float vD_{0.0f}, vQ_{0.0f};
    float vAlpha_{0.0f}, vBeta_{0.0f};

    PiController piD_;
    PiController piQ_;
    PiController piSpeed_;
};

} // namespace control

#endif // FOC_HPP_INCLUDED
