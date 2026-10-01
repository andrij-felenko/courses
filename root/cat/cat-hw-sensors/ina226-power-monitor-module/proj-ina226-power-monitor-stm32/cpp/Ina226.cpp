#include "Ina226.hpp"
#include <cmath>

Ina226::Ina226(II2cBus& bus, uint8_t address)
    : bus_(bus), address_(address) {}

bool Ina226::begin(const Config& config) {
    // 1. Програмний скид для встановлення регістрів у початковий стан
    if (!reset()) {
        return false;
    }

    // 2. Перевірка ID виробника та ID пристрою
    if (!checkDeviceID()) {
        return false;
    }

    // 3. Розрахунок та запис калібрувального коефіцієнта
    if (!setCalibration(config.shuntResistanceOhms, config.maxExpectedCurrentA)) {
        return false;
    }

    // 4. Формування та запис регістра конфігурації
    uint16_t configReg = static_cast<uint16_t>(config.avg) |
                         static_cast<uint16_t>(config.vbusTime) |
                         static_cast<uint16_t>(config.vshTime) |
                         static_cast<uint16_t>(config.mode);

    return bus_.writeRegister16(address_, static_cast<uint8_t>(Register::Config), configReg);
}

bool Ina226::reset() {
    // Біт 15 в регістрі Config виконує м'яке скидання пристрою
    constexpr uint16_t RST_BIT = 0x8000;
    return bus_.writeRegister16(address_, static_cast<uint8_t>(Register::Config), RST_BIT);
}

bool Ina226::checkDeviceID() {
    uint16_t mfgID = 0;
    uint16_t dieID = 0;

    if (!bus_.readRegister16(address_, static_cast<uint8_t>(Register::ManufacturerID), mfgID)) {
        return false;
    }
    if (!bus_.readRegister16(address_, static_cast<uint8_t>(Register::DieID), dieID)) {
        return false;
    }

    // Очікувані значення для INA226: ID виробника 0x5449 ("TI"), ID кристала 0x2260
    constexpr uint16_t EXPECTED_MFG_ID = 0x5449;
    constexpr uint16_t EXPECTED_DIE_ID_MASK = 0xFFF0;
    constexpr uint16_t EXPECTED_DIE_ID = 0x2260;

    return (mfgID == EXPECTED_MFG_ID) && ((dieID & EXPECTED_DIE_ID_MASK) == EXPECTED_DIE_ID);
}

bool Ina226::setCalibration(double shuntResistanceOhms, double maxExpectedCurrentA) {
    if (shuntResistanceOhms <= 0.0 || maxExpectedCurrentA <= 0.0) {
        return false;
    }

    // Крок 1: Розрахунок мінімального розряду струму (Current LSB)
    // Розрядність регістра струму - 15 біт + знак (32768)
    currentLSB_ = maxExpectedCurrentA / 32768.0;

    // Крок 2: Розрахунок розряду потужності (Power LSB = 25 * Current LSB)
    powerLSB_ = 25.0 * currentLSB_;

    // Крок 3: Розрахунок калібрувального значення CAL
    // Формула TI: CAL = trunc(0.00512 / (Current_LSB * R_shunt))
    double rawCal = CAL_FIXED_FACTOR / (currentLSB_ * shuntResistanceOhms);
    if (rawCal <= 0.0 || rawCal > 65535.0) {
        return false; // Значення виходить за межі 16-бітного регістра
    }

    calValue_ = static_cast<uint16_t>(std::floor(rawCal));

    // Запис у регістр Calibration
    return bus_.writeRegister16(address_, static_cast<uint8_t>(Register::Calibration), calValue_);
}

bool Ina226::configureAlert(const AlertConfig& alertConfig) {
    uint16_t rawLimit = 0;

    // Перерахунок порогового фізичного значення у дискрети відповідного регістра
    switch (alertConfig.mode) {
        case AlertMode::ShuntOverVoltage:
        case AlertMode::ShuntUnderVoltage: {
            // Порогове значення в Вольтах переводиться в дискрети з LSB = 2.5 мкВ
            double count = alertConfig.limitValue / SHUNT_VOLTAGE_LSB_V;
            rawLimit = static_cast<uint16_t>(static_cast<int16_t>(count));
            break;
        }
        case AlertMode::BusOverVoltage:
        case AlertMode::BusUnderVoltage: {
            // Порогове значення в Вольтах переводиться в дискрети з LSB = 1.25 мВ
            double count = alertConfig.limitValue / BUS_VOLTAGE_LSB_V;
            rawLimit = static_cast<uint16_t>(count);
            break;
        }
        case AlertMode::PowerOverLimit: {
            // Порогове значення у Ватах переводиться в дискрети з LSB = powerLSB_
            if (powerLSB_ <= 0.0) {
                return false;
            }
            double count = alertConfig.limitValue / powerLSB_;
            rawLimit = static_cast<uint16_t>(count);
            break;
        }
        case AlertMode::ConversionReady:
        case AlertMode::None:
            rawLimit = 0;
            break;
    }

    // 1. Запис значення порогу у регістр Alert Limit
    if (!bus_.writeRegister16(address_, static_cast<uint8_t>(Register::AlertLimit), rawLimit)) {
        return false;
    }

    // 2. Формування регістра Mask/Enable
    uint16_t maskValue = static_cast<uint16_t>(alertConfig.mode) |
                         static_cast<uint16_t>(alertConfig.polarity) |
                         static_cast<uint16_t>(alertConfig.latch);

    return bus_.writeRegister16(address_, static_cast<uint8_t>(Register::MaskEnable), maskValue);
}

bool Ina226::readBusVoltage(double& voltageV) {
    uint16_t raw = 0;
    if (!bus_.readRegister16(address_, static_cast<uint8_t>(Register::BusVoltage), raw)) {
        return false;
    }
    // Напруга шини: беззнакове 16-бітне число, LSB = 1.25 мВ (0.00125 В)
    voltageV = static_cast<double>(raw) * BUS_VOLTAGE_LSB_V;
    return true;
}

bool Ina226::readShuntVoltage(double& voltagemV) {
    uint16_t rawReg = 0;
    if (!bus_.readRegister16(address_, static_cast<uint8_t>(Register::ShuntVoltage), rawReg)) {
        return false;
    }
    // Напруга на шунті: знакове 16-бітне число (два доповнення), LSB = 2.5 мкВ
    int16_t raw = static_cast<int16_t>(rawReg);
    voltagemV = (static_cast<double>(raw) * SHUNT_VOLTAGE_LSB_V) * 1000.0; // В -> мВ
    return true;
}

bool Ina226::readCurrent(double& currentA) {
    uint16_t rawReg = 0;
    if (!bus_.readRegister16(address_, static_cast<uint8_t>(Register::Current), rawReg)) {
        return false;
    }
    // Струм: знакове 16-бітне число, результат множиться на Current LSB
    int16_t raw = static_cast<int16_t>(rawReg);
    currentA = static_cast<double>(raw) * currentLSB_;
    return true;
}

bool Ina226::readPower(double& powerW) {
    uint16_t raw = 0;
    if (!bus_.readRegister16(address_, static_cast<uint8_t>(Register::Power), raw)) {
        return false;
    }
    // Потужність: беззнакове 16-бітне число, результат множиться на Power LSB
    powerW = static_cast<double>(raw) * powerLSB_;
    return true;
}

bool Ina226::clearAlert(uint16_t* outMaskFlags) {
    uint16_t maskReg = 0;
    // Читання регістра Mask/Enable скидає тригер лінії ALERT та біт AFF
    bool status = bus_.readRegister16(address_, static_cast<uint8_t>(Register::MaskEnable), maskReg);
    if (status && outMaskFlags != nullptr) {
        *outMaskFlags = maskReg;
    }
    return status;
}

bool Ina226::readMeasurements(Measurements& outMeasurements) {
    if (!readBusVoltage(outMeasurements.busVoltageV)) return false;
    if (!readShuntVoltage(outMeasurements.shuntVoltagemV)) return false;
    if (!readCurrent(outMeasurements.currentA)) return false;
    if (!readPower(outMeasurements.powerW)) return false;

    // Зчитування статусного регістра для перевірки прапорців OVF, AFF, CVRF
    uint16_t maskReg = 0;
    if (clearAlert(&maskReg)) {
        outMeasurements.overflow        = (maskReg & 0x0004) != 0; // Біт 2: OVF
        outMeasurements.alertTriggered  = (maskReg & 0x0010) != 0; // Біт 4: AFF
        outMeasurements.conversionReady = (maskReg & 0x0008) != 0; // Біт 3: CVRF
    }

    return true;
}
