#include <cstdint>
#include <array>

#pragma pack(push, 1)
struct ClickHouseCompressedBlockHeader {
    std::array<std::uint8_t, 16> cityhash128_checksum{}; /* 128-бітний CityHash128 */
    std::uint8_t                 compression_method{0};  /* 0x82 = LZ4, 0x90 = ZSTD */
    std::uint32_t                compressed_size_with_header{0};
    std::uint32_t                uncompressed_size{0};
};
#pragma pack(pop)
