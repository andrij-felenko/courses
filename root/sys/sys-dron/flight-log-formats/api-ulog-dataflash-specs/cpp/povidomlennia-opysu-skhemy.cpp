// C++20
#include <cstdint>
#include <array>

#pragma pack(push, 1)
struct DataFlash_FMT_Payload {
    uint8_t  type{0};
    uint8_t  length{0};
    std::array<char, 4>  name{};
    std::array<char, 16> format{};
    std::array<char, 64> columns{};
};
#pragma pack(pop)
