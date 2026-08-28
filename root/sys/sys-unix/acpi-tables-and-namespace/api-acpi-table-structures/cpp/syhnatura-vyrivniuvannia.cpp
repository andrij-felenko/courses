// C++ Idiomatic Definition (C++20 layout)
#include <cstdint>
#include <array>
#include <span>

#pragma pack(push, 1)

struct alignas(1) RsdpDescriptorV1 {
    std::array<char, 8> signature;     // "RSD PTR "
    std::uint8_t        checksum;      // Checksum of first 20 bytes
    std::array<char, 6> oem_id;        // OEM String
    std::uint8_t        revision;      // 0 for v1.0, 2 for v2.0+
    std::uint32_t       rsdt_address;  // 32-bit physical address
};

struct alignas(1) RsdpDescriptorV2 {
    RsdpDescriptorV1  v1;
    std::uint32_t     length;          // 36 bytes
    std::uint64_t     xsdt_address;    // 64-bit physical address
    std::uint8_t      extended_checksum; // Checksum of entire 36 bytes
    std::array<std::uint8_t, 3> reserved;
};

#pragma pack(pop)
