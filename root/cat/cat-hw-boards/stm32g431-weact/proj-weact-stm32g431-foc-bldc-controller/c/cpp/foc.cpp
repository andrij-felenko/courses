#include "foc.hpp"
#include <cmath>

namespace control {

constexpr float SQRT3 = 1.73205080756887729353f;

void FocController::init(float busVoltage, uint16_t pwmPeriod) noexcept {
    busVoltage_ = (busVoltage > 1.0f) ? busVoltage : 24.0f;
    pwmPeriod_ = pwmPeriod;

    const float maxVoltage = busVoltage_ / SQRT3;
    piD_ = PiController(2.5f, 500.0f, -maxVoltage, maxVoltage);
    piQ_ = PiController(2.5f, 500.0f, -maxVoltage, maxVoltage);
    piSpeed_ = PiController(0.05f, 1.2f, -10.0f, 10.0f);
}

std::pair<float, float> FocController::clarkeTransform(float iA, float iB) const noexcept {
    const float iAlpha = iA;
    const float iBeta = (iA + 2.0f * iB) * (1.0f / SQRT3);
    return { iAlpha, iBeta };
}

std::pair<float, float> FocController::parkTransform(float iAlpha, float iBeta, float cosTh, float sinTh) const noexcept {
    const float iD =  iAlpha * cosTh + iBeta * sinTh;
    const float iQ = -iAlpha * sinTh + iBeta * cosTh;
    return { iD, iQ };
}

std::pair<float, float> FocController::inverseParkTransform(float vD, float vQ, float cosTh, float sinTh) const noexcept {
    const float vAlpha = vD * cosTh - vQ * sinTh;
    const float vBeta  = vD * sinTh + vQ * cosTh;
    return { vAlpha, vBeta };
}

std::tuple<uint16_t, uint16_t, uint16_t> FocController::calculateSvpwm(float vAlpha, float vBeta) const noexcept {
    const float vA = vAlpha;
    const float vB = -0.5f * vAlpha + (SQRT3 * 0.5f) * vBeta;
    const float vC = -0.5f * vAlpha - (SQRT3 * 0.5f) * vBeta;

    const float vMax = std::max({vA, vB, vC});
    const float vMin = std::min({vA, vB, vC});
    const float vZero = 0.5f * (vMax + vMin);

    const float dA = std::clamp(((vA - vZero) / busVoltage_) + 0.5f, 0.0f, 1.0f);
    const float dB = std::clamp(((vB - vZero) / busVoltage_) + 0.5f, 0.0f, 1.0f);
    const float dC = std::clamp(((vC - vZero) / busVoltage_) + 0.5f, 0.0f, 1.0f);

    return {
        static_cast<uint16_t>(dA * pwmPeriod_),
        static_cast<uint16_t>(dB * pwmPeriod_),
        static_cast<uint16_t>(dC * pwmPeriod_)
    };
}

void FocController::updateCurrentLoop(float electricalAngle, float dt, sys::McuPeripherals& periph) noexcept {
    const auto currents = periph.readPhaseCurrents();
    iA_ = currents.iA;
    iB_ = currents.iB;
    iC_ = currents.iC;

    const auto [cosTh, sinTh] = periph.computeCosSinCordic(electricalAngle);

    std::tie(iAlpha_, iBeta_) = clarkeTransform(iA_, iB_);
    std::tie(iD_, iQ_) = parkTransform(iAlpha_, iBeta_, cosTh, sinTh);

    vD_ = piD_.update(targetId_, iD_, dt);
    vQ_ = piQ_.update(targetIq_, iQ_, dt);

    std::tie(vAlpha_, vBeta_) = inverseParkTransform(vD_, vQ_, cosTh, sinTh);

    const auto [dutyA, dutyB, dutyC] = calculateSvpwm(vAlpha_, vBeta_);

    periph.setDutyCycles(dutyA, dutyB, dutyC);
}

void FocController::updateSpeedLoop(float measuredSpeed, float dt) noexcept {
    measuredSpeed_ = measuredSpeed;
    targetIq_ = piSpeed_.update(targetSpeed_, measuredSpeed_, dt);
}

} // namespace control
