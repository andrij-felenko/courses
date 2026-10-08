#include <cstdint>
#include <cstddef>
#include <array>

class ModbusFramePacker {
public:
    static uint16_t calculateCRC16(const uint8_t* data, std::size_t length) {
        uint16_t crc = 0xFFFF;
        for (std::size_t i = 0; i < length; ++i) {
            crc ^= data[i];
            for (uint8_t j = 0; j < 8; ++j) {
                if (crc & 0x0001) {
                    crc = (crc >> 1) ^ 0xA001;
                } else {
                    crc >>= 1;
                }
            }
        }
        return crc;
    }

    static std::array<uint8_t, 8> packWriteSingleRegister(uint8_t slaveAddr, uint16_t regAddr, uint16_t value) {
        std::array<uint8_t, 8> frame{};
        frame[0] = slaveAddr;
        frame[1] = 0x06;
        frame[2] = static_cast<uint8_t>(regAddr >> 8);
        frame[3] = static_cast<uint8_t>(regAddr & 0xFF);
        frame[4] = static_cast<uint8_t>(value >> 8);
        frame[5] = static_cast<uint8_t>(value & 0xFF);

        uint16_t crc = calculateCRC16(frame.data(), 6);
        frame[6] = static_cast<uint8_t>(crc & 0xFF);
        frame[7] = static_cast<uint8_t>((crc >> 8) & 0xFF);

        return frame;
    }
};
