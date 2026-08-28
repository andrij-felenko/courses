#include <array>
#include <cstdint>
#include <cstring>
#include <span>

struct RfcUuid {
    std::array<uint8_t, 16> bytes{};
};

struct WindowsGuid {
    uint32_t data1;
    uint16_t data2;
    uint16_t data3;
    std::array<uint8_t, 8> data4;
};

[[nodiscard]] constexpr RfcUuid to_rfc_uuid(const WindowsGuid& src) noexcept {
    RfcUuid dst{};

    dst.bytes[0] = static_cast<uint8_t>(src.data1 >> 24);
    dst.bytes[1] = static_cast<uint8_t>(src.data1 >> 16);
    dst.bytes[2] = static_cast<uint8_t>(src.data1 >> 8);
    dst.bytes[3] = static_cast<uint8_t>(src.data1);

    dst.bytes[4] = static_cast<uint8_t>(src.data2 >> 8);
    dst.bytes[5] = static_cast<uint8_t>(src.data2);

    dst.bytes[6] = static_cast<uint8_t>(src.data3 >> 8);
    dst.bytes[7] = static_cast<uint8_t>(src.data3);

    for (size_t i = 0; i < 8; ++i) {
        dst.bytes[8 + i] = src.data4[i];
    }

    return dst;
}
