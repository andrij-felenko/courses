// C++ альтернатива: резервний масив з фіксованим розміром
#include <cstdint>
#include <array>

struct HardwareConfig {
    uint32_t baud_rate;
    uint8_t parity;
    uint8_t stop_bits;
    std::array<uint8_t, 10> reserved{}; // Захист загального розміру
};
