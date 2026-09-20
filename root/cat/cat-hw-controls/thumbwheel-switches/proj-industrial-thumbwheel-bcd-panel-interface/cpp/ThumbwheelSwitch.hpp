#pragma once

#include <cstdint>
#include <cstddef>

// Перелічення станів валідності BCD-коду
enum class BcdStatus : uint8_t {
    OK = 0,            // Код валідний (0..9)
    InvalidCode = 1,   // Транзитний або некоректний код (0xA..0xF)
    ContactError = 2   // Обрив або помилка комутації контактної групи
};

// Апаратна абстракція вводу-виводу для роботи з BCD-шиною та лініями сканування
class IGpioPort {
public:
    virtual ~IGpioPort() = default;

    // Зчитування 4-бітної BCD-тетради з кодової шини (повертає значення 0x0..0xF)
    virtual uint8_t readBcdNibble() const = 0;

    // Керування лінією стробування/сканування конкретної декади
    virtual void setStrobe(uint8_t digitIndex, bool active) = 0;
};

// Драйвер поодинокої декади BCD-перемикача
class ThumbwheelSwitch {
public:
    ThumbwheelSwitch(IGpioPort& gpio, 
                     uint8_t digitIndex, 
                     bool activeLow = false, 
                     bool complementary = false)
        : gpio_(gpio), 
          digitIndex_(digitIndex), 
          activeLow_(activeLow), 
          complementary_(complementary) {}

    // Зчитування та первинна перевірка BCD-тетради для цієї декади
    BcdStatus readRaw(uint8_t& outDigit) const {
        uint8_t raw = gpio_.readBcdNibble() & 0x0F;

        if (activeLow_) {
            raw = (~raw) & 0x0F;
        }

        if (complementary_) {
            raw = (~raw) & 0x0F;
        }

        outDigit = raw;

        // Валідація BCD-діапазону (0..9)
        if (raw > 9) {
            return BcdStatus::InvalidCode;
        }

        return BcdStatus::OK;
    }

    uint8_t getDigitIndex() const { return digitIndex_; }

private:
    IGpioPort& gpio_;
    uint8_t digitIndex_;
    bool activeLow_;
    bool complementary_;
};
