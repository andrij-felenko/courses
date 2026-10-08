#ifndef INA226_TYPES_HPP
#define INA226_TYPES_HPP

#include <cstdint>

namespace INA226 {

enum class Mode : uint8_t {
    PowerDown       = 0x00,
    ShuntTriggered  = 0x01,
    BusTriggered    = 0x02,
    AllTriggered    = 0x03,
    ShuntContinuous = 0x05,
    BusContinuous   = 0x06,
    AllContinuous   = 0x07
};

enum class ConvTime : uint8_t {
    Time_140us  = 0x00,
    Time_204us  = 0x01,
    Time_332us  = 0x02,
    Time_588us  = 0x03,
    Time_1100us = 0x04,
    Time_2116us = 0x05,
    Time_4156us = 0x06,
    Time_8244us = 0x07
};

enum class Averaging : uint8_t {
    Samples_1    = 0x00,
    Samples_4    = 0x01,
    Samples_16   = 0x02,
    Samples_64   = 0x03,
    Samples_128  = 0x04,
    Samples_256  = 0x05,
    Samples_512  = 0x06,
    Samples_1024 = 0x07
};

struct Config {
    Mode      mode         = Mode::AllContinuous;
    ConvTime  vshConvTime  = ConvTime::Time_1100us;
    ConvTime  vbusConvTime = ConvTime::Time_1100us;
    Averaging avgSamples   = Averaging::Samples_1;

    // Метод пакування конфігурації у 16-бітове значення регістру 00h
    uint16_t toRegisterValue() const {
        return (static_cast<uint16_t>(avgSamples) << 9) |
               (static_cast<uint16_t>(vbusConvTime) << 6) |
               (static_cast<uint16_t>(vshConvTime) << 3) |
               static_cast<uint16_t>(mode);
    }
};

} // namespace INA226

#endif // INA226_TYPES_HPP
