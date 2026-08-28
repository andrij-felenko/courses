// Ідіоматичний формат тегованого кадру на мові C++ з типізованим переліком
#include <cstdint>

enum class SensorTagType : uint8_t {
    Gyroscope   = 0x01,
    Accelerometer = 0x02,
    Temperature = 0x03,
    Timestamp   = 0x04
};

#pragma pack(push, 1)
struct SensorFifoPacket {
    uint8_t tag;
    int16_t x;
    int16_t y;
    int16_t z;

    [[nodiscard]] SensorTagType type() const noexcept {
        return static_cast<SensorTagType>((tag >> 3) & 0x1F);
    }
};
#pragma pack(pop)
