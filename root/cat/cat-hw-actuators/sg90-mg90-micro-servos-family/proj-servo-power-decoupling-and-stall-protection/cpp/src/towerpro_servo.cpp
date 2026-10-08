#include "towerpro_servo.hpp"
#include <algorithm>
#include <cmath>

namespace towerpro {

ServoProfile TowerProServo::getProfile(ServoModel model) {
    switch (model) {
        case ServoModel::SG90:
            return ServoProfile{
                "TowerPro SG90",
                500,    // minPulseUs
                2400,   // maxPulseUs
                180.0f, // maxAngleDeg
                500.0f, // stallCurrentThresholdmA
                300,    // stallTimeoutMs
                false,  // isDigital
                false   // isMetalGear
            };
        case ServoModel::SG92R:
            return ServoProfile{
                "TowerPro SG92R",
                500,    // minPulseUs
                2400,   // maxPulseUs
                180.0f, // maxAngleDeg
                600.0f, // stallCurrentThresholdmA
                250,    // stallTimeoutMs
                false,  // isDigital
                false   // isMetalGear
            };
        case ServoModel::MG90S:
            return ServoProfile{
                "TowerPro MG90S",
                500,    // minPulseUs
                2500,   // maxPulseUs
                180.0f, // maxAngleDeg
                750.0f, // stallCurrentThresholdmA
                500,    // stallTimeoutMs
                false,  // isDigital
                true    // isMetalGear
            };
        case ServoModel::MG90D:
            return ServoProfile{
                "TowerPro MG90D",
                500,    // minPulseUs
                2500,   // maxPulseUs
                180.0f, // maxAngleDeg
                950.0f, // stallCurrentThresholdmA
                400,    // stallTimeoutMs
                true,   // isDigital
                true    // isMetalGear
            };
    }
    return ServoProfile{"Unknown", 500, 2500, 180.0f, 500.0f, 300, false, false};
}

bool TowerProServo::begin(const ServoConfig& config) {
    config_ = config;
    profile_ = getProfile(config.model);

    if (config.overrideMinPulseUs > 0) profile_.minPulseUs = config.overrideMinPulseUs;
    if (config.overrideMaxPulseUs > 0) profile_.maxPulseUs = config.overrideMaxPulseUs;
    if (config.overrideStallCurrentLimitmA > 0.0f) profile_.stallCurrentThresholdmA = config.overrideStallCurrentLimitmA;
    if (config.overrideStallTimeoutMs > 0) profile_.stallTimeoutMs = config.overrideStallTimeoutMs;

    if (!pwmDriver_.begin(config.pwmPin)) {
        return false;
    }

    if (!currentSensor_.begin(config.adcConfig)) {
        pwmDriver_.detach();
        return false;
    }

    emergencyStopped_ = false;
    overloaded_ = false;
    overloadStartTimeMs_ = 0;
    
    setAngle(90.0f);
    return true;
}

uint16_t TowerProServo::angleToMicroseconds(float angle) const {
    float clampedAngle = std::clamp(angle, 0.0f, profile_.maxAngleDeg);
    float pulseRange = static_cast<float>(profile_.maxPulseUs - profile_.minPulseUs);
    float pulse = static_cast<float>(profile_.minPulseUs) + (clampedAngle / profile_.maxAngleDeg) * pulseRange;
    return static_cast<uint16_t>(std::round(pulse));
}

float TowerProServo::microsecondsToAngle(uint16_t pulseUs) const {
    uint16_t clampedPulse = std::clamp(pulseUs, profile_.minPulseUs, profile_.maxPulseUs);
    float pulseRange = static_cast<float>(profile_.maxPulseUs - profile_.minPulseUs);
    return ((clampedPulse - profile_.minPulseUs) / pulseRange) * profile_.maxAngleDeg;
}

void TowerProServo::setAngle(float degrees) {
    if (emergencyStopped_) {
        return;
    }
    targetAngleDeg_ = std::clamp(degrees, 0.0f, profile_.maxAngleDeg);
    currentPulseUs_ = angleToMicroseconds(targetAngleDeg_);
    pwmDriver_.writeMicroseconds(currentPulseUs_);
}

float TowerProServo::getAngle() const {
    return targetAngleDeg_;
}

void TowerProServo::writeMicroseconds(uint16_t pulseUs) {
    if (emergencyStopped_) {
        return;
    }
    currentPulseUs_ = std::clamp(pulseUs, profile_.minPulseUs, profile_.maxPulseUs);
    targetAngleDeg_ = microsecondsToAngle(currentPulseUs_);
    pwmDriver_.writeMicroseconds(currentPulseUs_);
}

uint16_t TowerProServo::readMicroseconds() const {
    return pwmDriver_.getPulseMicroseconds();
}

void TowerProServo::update(uint32_t currentTimeMs, uint32_t currentTimeUs) {
    currentSensor_.update(currentTimeUs);

    if (emergencyStopped_) {
        return;
    }

    float currentmA = currentSensor_.readCurrentmA();

    if (currentmA >= profile_.stallCurrentThresholdmA) {
        if (!overloaded_) {
            overloaded_ = true;
            overloadStartTimeMs_ = currentTimeMs;
            currentOverloadDurationMs_ = 0;
        } else {
            currentOverloadDurationMs_ = currentTimeMs - overloadStartTimeMs_;
        }

        if (currentOverloadDurationMs_ >= profile_.stallTimeoutMs) {
            emergencyStopped_ = true;
            detach();

            if (emergencyCallback_) {
                emergencyCallback_(config_.model, currentmA, currentOverloadDurationMs_);
            }
        }
    } else {
        overloaded_ = false;
        overloadStartTimeMs_ = 0;
        currentOverloadDurationMs_ = 0;
    }
}

void TowerProServo::detach() {
    pwmDriver_.detach();
}

void TowerProServo::attach() {
    if (!emergencyStopped_) {
        pwmDriver_.attach();
    }
}

bool TowerProServo::isAttached() const {
    return pwmDriver_.isAttached();
}

bool TowerProServo::isOverloaded() const {
    return overloaded_;
}

bool TowerProServo::isEmergencyStopped() const {
    return emergencyStopped_;
}

void TowerProServo::resetEmergency() {
    emergencyStopped_ = false;
    overloaded_ = false;
    overloadStartTimeMs_ = 0;
    currentOverloadDurationMs_ = 0;
    attach();
}

void TowerProServo::setEmergencyCallback(EmergencyCallback callback) {
    emergencyCallback_ = callback;
}

float TowerProServo::getCurrentmA() const {
    return currentSensor_.readCurrentmA();
}

void TowerProServo::setSimulatedAdcRaw(uint16_t adcRaw) {
    currentSensor_.setSimulatedRawAdc(adcRaw);
}

} // namespace towerpro
