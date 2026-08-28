// Упакована бінарна структура кадру (C++20)
#include <cstdint>

struct alignas(1) SensorPacket {
    std::uint8_t  magic{0xA5};
    std::uint8_t  msg_type{0x01};
    std::uint16_t seq_num{0};
    std::uint32_t timestamp{0};
    std::int16_t  temperature{0};
    std::uint16_t humidity{0};
    std::uint16_t vbat_mv{0};
    std::uint16_t crc16{0};
};
