#include "rotary_dip_switch.hpp"

RotaryDipSwitch::RotaryDipSwitch(const IGpioReader& gpio,
                                 EncodingType encoding,
                                 std::chrono::milliseconds debounce_delay)
    : gpio_(gpio),
      encoding_(encoding),
      debounce_delay_(debounce_delay) {
    uint8_t initial_raw = readRawValue();
    last_raw_state_ = initial_raw;
    stable_state_ = initial_raw;
}

uint8_t RotaryDipSwitch::readRawValue() const {
    uint8_t raw_pins = gpio_.readPinGroup() & 0x0F;

    if (encoding_ == EncodingType::ComplementaryBinary) {
        // Інвертуємо біти для комплементарного кодування
        return (~raw_pins) & 0x0F;
    }

    return raw_pins;
}

uint8_t RotaryDipSwitch::update(std::chrono::steady_clock::time_point current_time) {
    uint8_t current_raw = readRawValue();

    // Перевірка зміни стану ліній (фіксація брязкоту або нового повороту)
    if (current_raw != last_raw_state_) {
        last_raw_state_ = current_raw;
        last_change_time_ = current_time;
    } else {
        // Якщо стан стабільний довше за таймаут дебаунсингу — фіксуємо стабільний стан
        if ((current_time - last_change_time_) >= debounce_delay_) {
            stable_state_ = current_raw;
        }
    }

    return getDecodedValue();
}

uint8_t RotaryDipSwitch::getDecodedValue() const {
    if (encoding_ == EncodingType::GrayCode) {
        return grayToBinary(stable_state_);
    }

    return stable_state_;
}

uint8_t RotaryDipSwitch::grayToBinary(uint8_t gray) {
    uint8_t binary = gray;
    uint8_t mask = gray >> 1;

    while (mask != 0) {
        binary ^= mask;
        mask >>= 1;
    }

    return binary & 0x0F;
}
