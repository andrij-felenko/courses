#include <stdint.h>

#pragma pack(push, 1)
struct ClickHouseCompressedBlockHeader {
    uint8_t  cityhash128_checksum[16]; /* 128-бітний хеш CityHash128 від заголовка та payload */
    uint8_t  compression_method;       /* 0x82 = LZ4, 0x90 = ZSTD, 0x02 = NONE */
    uint32_t compressed_size_with_header; /* Розмір стиснених даних + 9 байтів заголовка */
    uint32_t uncompressed_size;        /* Точний розмір розпакованих даних у байтах */
};
#pragma pack(pop)
