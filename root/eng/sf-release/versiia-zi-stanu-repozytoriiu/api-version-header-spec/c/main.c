#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define VERSION_HEADER_MAGIC 0x56455253U

#pragma pack(push, 4)
typedef struct {
    uint32_t magic;
    uint16_t struct_version;
    uint16_t flags;
    uint16_t major;
    uint16_t minor;
    uint16_t patch;
    uint16_t reserved;
    uint32_t commit_count;
    char     git_sha_short[8];
    uint64_t timestamp;
    char     tag_name[32];
    uint32_t crc32;
} version_descriptor_t;
#pragma pack(pop)

/* Обчислення стандарту CRC32 (IEEE 802.3) */
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (int j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
        }
    }
    return ~crc;
}

/* Валідація структури дескриптора */
bool validate_version_descriptor(const version_descriptor_t *desc) {
    if (!desc) return false;
    if (desc->magic != VERSION_HEADER_MAGIC) return false;
    if (desc->struct_version != 1U) return false;

    /* Обчислення контрольної суми перших 68 байтів структури */
    uint32_t expected_crc = calculate_crc32((const uint8_t *)desc, 68);
    return (desc->crc32 == expected_crc);
}
