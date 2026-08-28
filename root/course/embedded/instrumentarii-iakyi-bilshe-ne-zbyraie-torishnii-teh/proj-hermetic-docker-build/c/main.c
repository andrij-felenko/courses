#include <stdint.h>
#include <string.h>

/* Структура детермінованих метаданих прошивки у фіксованій секції Flash */
typedef struct {
    uint32_t magic;
    uint32_t build_timestamp;
    char     git_commit[16];
    char     toolchain_id[16];
    uint32_t image_crc32;
} __attribute__((packed)) firmware_meta_t;

#define META_MAGIC 0x544F4F4C /* 'TOOL' */

#ifndef SOURCE_DATE_EPOCH
#define SOURCE_DATE_EPOCH 0U
#endif

/* Розміщення у спеціальній секції .meta для аудиту без розбору всього ELF */
__attribute__((section(".meta"), used))
const firmware_meta_t g_firmware_meta = {
    .magic           = META_MAGIC,
    .build_timestamp = (uint32_t)SOURCE_DATE_EPOCH,
    .git_commit      = "a1b2c3d4e5f60718",
    .toolchain_id    = "gcc-13.2.arm",
    .image_crc32     = 0xDEADBEEFU
};

int verify_build_metadata(const firmware_meta_t *meta) {
    if (meta == NULL || meta->magic != META_MAGIC) {
        return -1;
    }
    /* Перевірка, що дата збірки є коректною міткою епохи */
    if (meta->build_timestamp == 0U) {
        return -2;
    }
    return 0;
}
