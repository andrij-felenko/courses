// C++20
#include <cstdint>
#include <array>

#pragma pack(push, 1)
struct DataFlash_PARM_Payload {
    uint64_t time_us{0};
    std::array<char, 16> name{};
    float    value{0.0f};
};
#pragma pack(pop)
