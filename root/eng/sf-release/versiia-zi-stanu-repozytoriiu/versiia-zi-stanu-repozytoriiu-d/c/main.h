#ifndef VERSION_INFO_H
#define VERSION_INFO_H

#include <stdint.h>
#include <stdbool.h>

#define VERSION_HEADER_MAGIC 0x56455253U /* 'VERS' */
#define VERSION_STRUCT_VER 1U

#define BUILD_FLAG_DIRTY      (1U << 0)
#define BUILD_FLAG_DEBUG      (1U << 1)
#define BUILD_FLAG_PRERELEASE (1U << 2)
#define BUILD_FLAG_CI         (1U << 3)

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
} version_info_t;
#pragma pack(pop)

#if defined(__GNUC__) || defined(__clang__)
__attribute__((section(".version_header"), used))
#endif
extern const version_info_t g_version_descriptor;

#endif /* VERSION_INFO_H */
