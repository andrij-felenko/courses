#include <cstdint>
#include <array>
#include <chrono>

struct alignas(16) TransitionLog {
    std::chrono::milliseconds timestamp{0};
    uint8_t  fromState{0};
    uint8_t  toState{0};
    uint8_t  eventId{0};
    uint8_t  retryCount{0};
    int8_t   rssiDbm{0};
    uint16_t cmeErrorCode{0};
    uint16_t voltageVbatMv{0};
    std::array<uint8_t, 2> reserved{};
};
