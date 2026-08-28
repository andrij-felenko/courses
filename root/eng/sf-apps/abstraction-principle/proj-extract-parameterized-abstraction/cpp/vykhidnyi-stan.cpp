#include <cstdint>
#include <cstddef>
#include <span>
#include <functional>

constexpr size_t GNSS_MAX_PAYLOAD = 128;
constexpr size_t OPTIC_MAX_PAYLOAD = 64;

// Парсер GNSS на C++ з прямим копіюванням логіки
struct GnssParser {
    uint8_t buf[GNSS_MAX_PAYLOAD];
    size_t len = 0;
    size_t expected_len = 0;
    uint8_t state = 0;
    uint8_t crc = 0;

    template <typename Callback>
    bool feed_byte(uint8_t byte, Callback&& on_frame) {
        switch (state) {
            case 0:
                if (byte == 0xAA) state = 1;
                break;
            case 1:
                if (byte == 0x55) { state = 2; len = 0; crc = 0; }
                else state = (byte == 0xAA) ? 1 : 0;
                break;
            case 2:
                expected_len = byte;
                crc ^= byte;
                state = (byte <= GNSS_MAX_PAYLOAD) ? 3 : 0;
                break;
            case 3:
                buf[len++] = byte;
                crc ^= byte;
                if (len == expected_len) state = 4;
                break;
            case 4:
                state = 0;
                if (crc == byte) {
                    on_frame(std::span<const uint8_t>(buf, len));
                    return true;
                }
                break;
        }
        return false;
    }
};

// Парсер давача на C++
struct OpticParser {
    uint8_t buf[OPTIC_MAX_PAYLOAD];
    size_t len = 0;
    size_t expected_len = 0;
    uint8_t state = 0;
    uint8_t crc = 0;

    template <typename Callback>
    bool feed_byte(uint8_t byte, Callback&& on_frame) {
        switch (state) {
            case 0:
                if (byte == 0x24) { state = 1; len = 0; crc = 0xFF; }
                break;
            case 1:
                expected_len = byte;
                crc += byte;
                state = (byte <= OPTIC_MAX_PAYLOAD) ? 2 : 0;
                break;
            case 2:
                buf[len++] = byte;
                crc += byte;
                if (len == expected_len) state = 3;
                break;
            case 3:
                state = 0;
                if (crc == byte) {
                    on_frame(std::span<const uint8_t>(buf, len));
                    return true;
                }
                break;
        }
        return false;
    }
};
