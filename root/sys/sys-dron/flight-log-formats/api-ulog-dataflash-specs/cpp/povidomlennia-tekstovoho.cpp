// C++20
#include <cstdint>
#include <array>

#pragma pack(push, 1)
struct DataFlash_MSG_Payload {
    uint64_t time_us{0};
    std::array<char, 50> message{};
};
#pragma pack(pop)
