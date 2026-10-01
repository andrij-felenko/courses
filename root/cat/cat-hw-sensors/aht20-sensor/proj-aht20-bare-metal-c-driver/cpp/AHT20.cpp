#include "AHT20.hpp"

AHT20::AHT20(I2CBus& bus, uint8_t address)
    : bus_(bus), address_(address) {}

bool AHT20::reset() {
    uint8_t status = 0;
    if (!readStatus(status)) {
        state_ = DriverState::Error;
        lastError_ = ErrorCode::BusError;
        return false;
    }

    // Якщо біт 3 дорівнює 0, давач потребує ініціалізації та калібрування
    if ((status & STATUS_CALIBRATED_MASK) == 0) {
        const uint8_t initCmd[3] = {CMD_INIT, 0x08, 0x00};
        if (!bus_.write(address_, initCmd, sizeof(initCmd))) {
            state_ = DriverState::Error;
            lastError_ = ErrorCode::BusError;
            return false;
        }
    }

    state_ = DriverState::Idle;
    lastError_ = ErrorCode::None;
    return true;
}

bool AHT20::startMeasurement(uint32_t currentTimeMs) {
    if (state_ == DriverState::Measuring) {
        return false;
    }

    const uint8_t measureCmd[3] = {CMD_MEASURE, 0x33, 0x00};
    if (!bus_.write(address_, measureCmd, sizeof(measureCmd))) {
        state_ = DriverState::Error;
        lastError_ = ErrorCode::BusError;
        return false;
    }

    measurementStartTimeMs_ = currentTimeMs;
    state_ = DriverState::Measuring;
    lastError_ = ErrorCode::None;
    return true;
}

bool AHT20::update(uint32_t currentTimeMs) {
    if (state_ != DriverState::Measuring) {
        return false;
    }

    // Перевірка часового інтервалу 80 мс
    if (currentTimeMs - measurementStartTimeMs_ < MEASUREMENT_DELAY_MS) {
        return false;
    }

    // Зчитування 7 байтів (1 байт стану, 5 байтів даних, 1 байт CRC)
    uint8_t buffer[7] = {0};
    if (!bus_.read(address_, buffer, sizeof(buffer))) {
        state_ = DriverState::Error;
        lastError_ = ErrorCode::BusError;
        lastMeasurement_.isValid = false;
        return false;
    }

    // Перевірка готовності давача (біт 7 бітового стану)
    const uint8_t status = buffer[0];
    if ((status & STATUS_BUSY_MASK) != 0) {
        return false;
    }

    // Валідація контрольної суми CRC-8
    const uint8_t expectedCrc = buffer[6];
    const uint8_t calculatedCrc = calculateCRC8(buffer, 6);
    if (calculatedCrc != expectedCrc) {
        state_ = DriverState::Error;
        lastError_ = ErrorCode::CrcMismatch;
        lastMeasurement_.isValid = false;
        return false;
    }

    // Парсинг 20-бітного сирого значення вологості
    const uint32_t rawHumidity = (static_cast<uint32_t>(buffer[1]) << 12) |
                                 (static_cast<uint32_t>(buffer[2]) << 4) |
                                 (static_cast<uint32_t>(buffer[3]) >> 4);

    // Парсинг 20-бітного сирого значення температури
    const uint32_t rawTemperature = ((static_cast<uint32_t>(buffer[3]) & 0x0F) << 16) |
                                    (static_cast<uint32_t>(buffer[4]) << 8) |
                                    static_cast<uint32_t>(buffer[5]);

    // Перетворення сирих даних у фізичні значення вологості й температури
    lastMeasurement_.humidity = (static_cast<float>(rawHumidity) / 1048576.0f) * 100.0f;
    lastMeasurement_.temperature = (static_cast<float>(rawTemperature) / 1048576.0f) * 200.0f - 50.0f;
    lastMeasurement_.isValid = true;

    state_ = DriverState::Idle;
    lastError_ = ErrorCode::None;
    return true;
}

Measurement AHT20::getMeasurement() const {
    return lastMeasurement_;
}

DriverState AHT20::getState() const {
    return state_;
}

ErrorCode AHT20::getLastError() const {
    return lastError_;
}

bool AHT20::readStatus(uint8_t& status) {
    return bus_.read(address_, &status, 1);
}

uint8_t AHT20::calculateCRC8(const uint8_t* data, std::size_t length) {
    uint8_t crc = 0xFF;
    for (std::size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x80) {
                crc = static_cast<uint8_t>((crc << 1) ^ 0x31);
            } else {
                crc = static_cast<uint8_t>(crc << 1);
            }
        }
    }
    return crc;
}
