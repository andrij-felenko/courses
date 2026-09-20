#include "Thumbwheel74HC165.hpp"

ThumbwheelStatus Thumbwheel74HC165::init(const ThumbwheelConfig& config) {
    if (config.decadesCount == 0 || config.decadesCount > 4) {
        return ThumbwheelStatus::ErrInvalidConfig;
    }
    if (!config.pinPl.write || !config.pinClk.write || !config.pinData.read) {
        return ThumbwheelStatus::ErrInvalidConfig;
    }

    config_ = config;

    // Встановлення початкових рівнів на керуючих виходах (PL=1, CLK=0)
    config_.pinPl.write(true);
    config_.pinClk.write(false);

    isInitialized_ = true;
    validatedValue_ = 0;
    filteredNibbles_.fill(0);
    candidateNibbles_.fill(0);
    debounceCounters_.fill(0);

    return ThumbwheelStatus::Ok;
}

uint16_t Thumbwheel74HC165::readRawShiftRegister() {
    uint16_t rawData = 0;

    // 1. Формування від'ємного стробу завантаження PL (Parallel Load)
    config_.pinPl.write(false);
    if (config_.pinPl.delayNs) {
        config_.pinPl.delayNs(20);
    }
    config_.pinPl.write(true);

    // 2. Послідовне зчитування бітів з лінії DATA при тактуванні CLK
    const uint8_t totalBits = config_.decadesCount * 4;
    for (uint8_t i = 0; i < totalBits; ++i) {
        rawData <<= 1;
        if (config_.pinData.read()) {
            rawData |= 0x0001;
        }

        config_.pinClk.write(true);
        if (config_.pinClk.delayNs) {
            config_.pinClk.delayNs(50);
        }
        config_.pinClk.write(false);
        if (config_.pinClk.delayNs) {
            config_.pinClk.delayNs(50);
        }
    }

    // 3. Інверсія бітів у разі схемотехніки з підтяжкою до VCC та контактами на GND
    if (config_.activeLowLogic) {
        rawData = static_cast<uint16_t>(~rawData);
    }

    return rawData;
}

bool Thumbwheel74HC165::parseAndValidateNibbles(uint16_t rawFrame, std::array<uint8_t, 4>& outNibbles) {
    bool allValid = true;
    for (int8_t i = config_.decadesCount - 1; i >= 0; --i) {
        uint8_t nibble = (rawFrame >> (i * 4)) & 0x0F;
        if (nibble > 9) {
            allValid = false; // Виявлено завадову або транзитну тетраду (10...15)
        }
        outNibbles[static_cast<size_t>(i)] = nibble;
    }
    return allValid;
}

void Thumbwheel74HC165::applyDebounceFilter(const std::array<uint8_t, 4>& currentNibbles) {
    uint16_t newCalculatedValue = 0;
    uint16_t multiplier = 1;

    for (size_t i = 0; i < config_.decadesCount; ++i) {
        if (currentNibbles[i] == candidateNibbles_[i]) {
            if (debounceCounters_[i] < config_.debounceThreshold) {
                debounceCounters_[i]++;
            }
        } else {
            candidateNibbles_[i] = currentNibbles[i];
            debounceCounters_[i] = 1;
        }

        // Якщо замір підтверджено необхідну кількість разів — оновлюємо відфільтровану тетраду
        if (debounceCounters_[i] >= config_.debounceThreshold) {
            filteredNibbles_[i] = candidateNibbles_[i];
        }

        newCalculatedValue += static_cast<uint16_t>(filteredNibbles_[i] * multiplier);
        multiplier *= 10;
    }

    // Сповіщення про зміну підтвердженої устави
    if (newCalculatedValue != validatedValue_) {
        uint16_t oldValue = validatedValue_;
        validatedValue_ = newCalculatedValue;
        if (onChangeCb_) {
            onChangeCb_(validatedValue_, oldValue);
        }
    }
}

ThumbwheelStatus Thumbwheel74HC165::poll() {
    if (!isInitialized_) {
        return ThumbwheelStatus::ErrInvalidConfig;
    }

    rawLatch_ = readRawShiftRegister();

    std::array<uint8_t, 4> currentNibbles{};
    bool isValid = parseAndValidateNibbles(rawLatch_, currentNibbles);

    if (!isValid) {
        return ThumbwheelStatus::ErrInvalidBcd;
    }

    applyDebounceFilter(currentNibbles);
    return ThumbwheelStatus::Ok;
}

uint8_t Thumbwheel74HC165::getNibble(uint8_t index) const noexcept {
    if (index < config_.decadesCount) {
        return filteredNibbles_[index];
    }
    return 0;
}
