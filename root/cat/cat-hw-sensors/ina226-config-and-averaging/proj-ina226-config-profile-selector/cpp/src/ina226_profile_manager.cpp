#include "ina226_profile_manager.hpp"
#include <cmath>
#include <string>

namespace ina226 {

Ina226ProfileManager::Ina226ProfileManager(II2cBus& i2cBus,
                                             uint8_t i2cAddress,
                                             double shuntResistorOhms,
                                             double maxExpectedCurrentA)
    : bus_(i2cBus),
      address_(i2cAddress),
      shuntResistorOhms_(shuntResistorOhms),
      maxExpectedCurrentA_(maxExpectedCurrentA) {}

bool Ina226ProfileManager::begin() {
    // 1. Проведення програмного скидання пристрою
    if (!reset()) {
        return false;
    }

    // 2. Перевірка Manufacturer ID (0x5449 = "TI") та Die ID (0x2260)
    uint16_t mfgId = 0;
    uint16_t dieId = 0;
    if (!readRegister(Register::ManufacturerId, mfgId) || mfgId != 0x5449) {
        return false;
    }
    if (!readRegister(Register::DieId, dieId) || (dieId & 0xFFF0) != 0x2260) {
        return false;
    }

    // 3. Калібрування для розрахунку струму та потужності
    if (!configureCalibration(maxExpectedCurrentA_)) {
        return false;
    }

    // 4. Застосування початкового профілю за замовчуванням
    return setProfile(currentProfile_);
}

bool Ina226ProfileManager::reset() {
    constexpr uint16_t RESET_BIT = 0x8000;
    return writeRegister(Register::Configuration, RESET_BIT);
}

bool Ina226ProfileManager::configureCalibration(double maxCurrentAmperes) {
    if (maxCurrentAmperes <= 0.0 || shuntResistorOhms_ <= 0.0) {
        return false;
    }

    maxExpectedCurrentA_ = maxCurrentAmperes;

    // Крок LSB струму: Current_LSB = Max_Current / 2^15
    currentLsb_ = maxExpectedCurrentA_ / 32768.0;

    // Формула з даташиту: CAL = trunc(0.00512 / (Current_LSB * Rshunt))
    double cal = 0.00512 / (currentLsb_ * shuntResistorOhms_);
    calibrationValue_ = static_cast<uint16_t>(std::trunc(cal));

    if (calibrationValue_ == 0) {
        return false;
    }

    return writeRegister(Register::Calibration, calibrationValue_);
}

bool Ina226ProfileManager::setProfile(const SamplingProfile& profile) {
    Ina226RegisterConfig cfg = profile.toRegisterConfig();
    uint16_t rawConfig = cfg.toRawValue();

    if (!writeRegister(Register::Configuration, rawConfig)) {
        return false;
    }

    currentProfile_ = profile;
    return true;
}

bool Ina226ProfileManager::setAlertMask(uint16_t maskFlags, uint16_t alertLimitRaw) {
    // Спочатку записуємо порогове значення у відповідний регістр
    if (!writeRegister(Register::AlertLimit, alertLimitRaw)) {
        return false;
    }
    // Записуємо бітові маски активації джерел переривання
    return writeRegister(Register::MaskEnable, maskFlags);
}

bool Ina226ProfileManager::setAdaptiveThresholds(double highCurrentThresholdA,
                                                 const SamplingProfile& dynamicProfile,
                                                 const SamplingProfile& steadyProfile) {
    if (highCurrentThresholdA <= 0.0) {
        return false;
    }

    highCurrentThresholdA_ = highCurrentThresholdA;
    dynamicProfile_ = dynamicProfile;
    steadyProfile_ = steadyProfile;
    adaptiveEnabled_ = true;

    // Встановлюємо стаціонарний профіль як базовий
    return setProfile(steadyProfile_);
}

void Ina226ProfileManager::handleAlertInterrupt() {
    uint16_t maskEnableVal = 0;
    if (!readRegister(Register::MaskEnable, maskEnableVal)) {
        return;
    }

    // Зчитуємо поточні параметри електричного кола
    double busVolt = 0.0;
    double shuntMv = 0.0;
    double currentA = 0.0;
    double powerW = 0.0;

    readBusVoltage(busVolt);
    readShuntVoltage(shuntMv);
    readCurrent(currentA);
    readPower(powerW);

    // Адаптивне перемикання профілів з урахуванням гістерезису (15%)
    if (adaptiveEnabled_) {
        const double hysteresisLowerThreshold = highCurrentThresholdA_ * 0.85;

        if (currentA > highCurrentThresholdA_ &&
            std::string(currentProfile_.name) != dynamicProfile_.name) {
            
            SamplingProfile oldProfile = currentProfile_;
            if (setProfile(dynamicProfile_)) {
                if (profileChangeCallback_) {
                    profileChangeCallback_(oldProfile, dynamicProfile_);
                }
            }
        } else if (currentA <= hysteresisLowerThreshold &&
                   std::string(currentProfile_.name) != steadyProfile_.name) {
            
            SamplingProfile oldProfile = currentProfile_;
            if (setProfile(steadyProfile_)) {
                if (profileChangeCallback_) {
                    profileChangeCallback_(oldProfile, steadyProfile_);
                }
            }
        }
    }

    // Визначення типу події переривання
    AlertEventType eventType = AlertEventType::Unknown;
    if (maskEnableVal & AlertStatusFlag::CONVR_READY) {
        eventType = AlertEventType::ConversionReady;
    } else if (maskEnableVal & AlertStatusFlag::ALERT_FUNCTION) {
        if (maskEnableVal & AlertMask::SHUNT_OVER_LIMIT) {
            eventType = AlertEventType::OverCurrentLimit;
        } else if (maskEnableVal & AlertMask::BUS_OVER_LIMIT) {
            eventType = AlertEventType::BusOverVoltage;
        } else if (maskEnableVal & AlertMask::POWER_OVER_LIMIT) {
            eventType = AlertEventType::PowerLimitExceeded;
        }
    } else if (maskEnableVal & AlertStatusFlag::MATH_OVERFLOW) {
        eventType = AlertEventType::MathOverflow;
    }

    // Виклик зворотного виклику для сповіщення зовнішнього коду
    if (alertCallback_) {
        AlertEvent event{
            eventType,
            currentA,
            busVolt,
            shuntMv,
            powerW,
            maskEnableVal
        };
        alertCallback_(event);
    }
}

bool Ina226ProfileManager::readBusVoltage(double& voltageVolts) {
    uint16_t rawBus = 0;
    if (!readRegister(Register::BusVoltage, rawBus)) {
        return false;
    }
    // LSB = 1.25 мВ = 0.00125 В
    voltageVolts = static_cast<double>(rawBus) * 0.00125;
    return true;
}

bool Ina226ProfileManager::readShuntVoltage(double& voltageMv) {
    uint16_t rawVal = 0;
    if (!readRegister(Register::ShuntVoltage, rawVal)) {
        return false;
    }
    // Знаковий 16-бітний результат, LSB = 2.5 мкВ = 0.0025 мВ
    auto rawShunt = static_cast<int16_t>(rawVal);
    voltageMv = static_cast<double>(rawShunt) * 0.0025;
    return true;
}

bool Ina226ProfileManager::readCurrent(double& currentAmperes) {
    uint16_t rawVal = 0;
    if (!readRegister(Register::Current, rawVal)) {
        return false;
    }
    // Знаковий 16-бітний результат: Current = RawCurrent * Current_LSB
    auto rawCurrent = static_cast<int16_t>(rawVal);
    currentAmperes = static_cast<double>(rawCurrent) * currentLsb_;
    return true;
}

bool Ina226ProfileManager::readPower(double& powerWatts) {
    uint16_t rawPower = 0;
    if (!readRegister(Register::Power, rawPower)) {
        return false;
    }
    // Power = RawPower * 25 * Current_LSB
    powerWatts = static_cast<double>(rawPower) * 25.0 * currentLsb_;
    return true;
}

bool Ina226ProfileManager::writeRegister(Register reg, uint16_t value) {
    return bus_.writeRegister16(address_, static_cast<uint8_t>(reg), value);
}

bool Ina226ProfileManager::readRegister(Register reg, uint16_t& value) {
    return bus_.readRegister16(address_, static_cast<uint8_t>(reg), value);
}

} // namespace ina226
