// C++20
#include <cstdint>
#include <array>

#pragma pack(push, 1)
struct DataFlash_FMT {
    uint8_t  head1{0xA3};
    uint8_t  head2{0x95};
    uint8_t  msg_type{0x80};
    uint8_t  type{0};
    uint8_t  length{0};
    std::array<char, 4>  name{};
    std::array<char, 16> format{};
    std::array<char, 64> columns{};
};
#pragma pack(pop)
