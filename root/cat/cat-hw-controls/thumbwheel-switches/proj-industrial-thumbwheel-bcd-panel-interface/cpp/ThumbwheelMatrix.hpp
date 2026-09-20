#pragma once

#include "ThumbwheelSwitch.hpp"
#include <cstdint>
#include <cstddef>
#include <array>

// Матричний драйвер багаторадного блоку декадних перемикачів
template <std::size_t MaxDigits>
class ThumbwheelMatrix {
public:
    ThumbwheelMatrix(IGpioPort& gpio, 
                     std::size_t digitCount, 
                     uint8_t debounceThreshold = 5,
                     bool activeLow = false,
                     bool complementary = false)
        : gpio_(gpio),
          digitCount_(digitCount > MaxDigits ? MaxDigits : digitCount),
          debounceThreshold_(debounceThreshold),
          activeLow_(activeLow),
          complementary_(complementary),
          lastValidValue_(0),
          valueChanged_(false) {
        
        stableBcd_.fill(0);
        candidateBcd_.fill(0);
        bounceCounter_.fill(0);
        digitStatus_.fill(BcdStatus::OK);
    }

    // Ініціалізація та очищення внутрішніх буферів
    void init() {
        stableBcd_.fill(0);
        candidateBcd_.fill(0);
        bounceCounter_.fill(0);
        digitStatus_.fill(BcdStatus::OK);
        lastValidValue_ = 0;
        valueChanged_ = false;
    }

    // Один крок матричного сканування та фільтрації (викликати в таймерному циклі)
    bool scan() {
        bool anyChanged = false;

        for (std::size_t i = 0; i < digitCount_; ++i) {
            // Активація лінії сканування i-ї декади
            gpio_.setStrobe(static_cast<uint8_t>(i), true);

            ThumbwheelSwitch sw(gpio_, static_cast<uint8_t>(i), activeLow_, complementary_);
            uint8_t rawValue = 0;
            BcdStatus status = sw.readRaw(rawValue);

            // Деактивація лінії сканування
            gpio_.setStrobe(static_cast<uint8_t>(i), false);

            digitStatus_[i] = status;

            // Якщо отримано інвалідний BCD-код (транзитний стан), скидаємо лічильник
            if (status != BcdStatus::OK) {
                bounceCounter_[i] = 0;
                continue;
            }

            // Цифрова фільтрація брязкоту (Debouncing)
            if (rawValue == candidateBcd_[i]) {
                if (bounceCounter_[i] < debounceThreshold_) {
                    bounceCounter_[i]++;
                    if (bounceCounter_[i] == debounceThreshold_) {
                        if (stableBcd_[i] != rawValue) {
                            stableBcd_[i] = rawValue;
                            anyChanged = true;
                        }
                    }
                }
            } else {
                candidateBcd_[i] = rawValue;
                bounceCounter_[i] = 0;
            }
        }

        if (anyChanged) {
            lastValidValue_ = calculateValue();
            valueChanged_ = true;
        } else {
            valueChanged_ = false;
        }

        return valueChanged_;
    }

    // Повертає підсумкове цілочисельне значення уставки
    uint32_t getValue() const {
        return lastValidValue_;
    }

    // Прапорець зміни значення при останньому опитуванні
    bool isValueChanged() const {
        return valueChanged_;
    }

    // Повертає статус валідності для вибраної декади
    BcdStatus getDigitStatus(std::size_t index) const {
        if (index < MaxDigits) {
            return digitStatus_[index];
        }
        return BcdStatus::ContactError;
    }

    // Повертає підтверджене BCD-значення конкретної декади
    uint8_t getStableDigit(std::size_t index) const {
        if (index < MaxDigits) {
            return stableBcd_[index];
        }
        return 0;
    }

private:
    // Математичний розрахунок підсумкового значення: Sum(BCD[i] * 10^i)
    uint32_t calculateValue() const {
        uint32_t result = 0;
        uint32_t multiplier = 1;

        for (std::size_t i = 0; i < digitCount_; ++i) {
            result += static_cast<uint32_t>(stableBcd_[i]) * multiplier;
            multiplier *= 10;
        }

        return result;
    }

    IGpioPort& gpio_;
    std::size_t digitCount_;
    uint8_t debounceThreshold_;
    bool activeLow_;
    bool complementary_;

    std::array<uint8_t, MaxDigits> stableBcd_;
    std::array<uint8_t, MaxDigits> candidateBcd_;
    std::array<uint8_t, MaxDigits> bounceCounter_;
    std::array<BcdStatus, MaxDigits> digitStatus_;

    uint32_t lastValidValue_;
    bool valueChanged_;
};
