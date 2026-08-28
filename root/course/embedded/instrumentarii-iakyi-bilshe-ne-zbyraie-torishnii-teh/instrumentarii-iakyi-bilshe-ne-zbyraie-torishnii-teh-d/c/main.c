#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Фіксована структура опису релізу, що розміщується за фіксованим зсувом */
typedef struct {
    uint32_t magic;             /* Сигнатура структури: 'RELM' (0x4D4C4552) */
    uint32_t build_timestamp;   /* Фіксована дата з SOURCE_DATE_EPOCH */
    uint8_t  git_hash[20];      /* Точний SHA-1 коміту Git */
    uint8_t  toolchain_hash[8]; /* Перші 8 байтів хешу контейнера OCI */
    uint32_t firmware_crc32;    /* Контрольна сума бінарного коду */
    uint32_t reserved;
} __attribute__((packed)) release_metadata_t;

#define RELEASE_META_MAGIC 0x4D4C4552U

#ifndef SOURCE_DATE_EPOCH
#define SOURCE_DATE_EPOCH 0U
#endif

/* Розміщення у спеціальній секції .meta_header через скрипт компонувальника */
__attribute__((section(".meta_header"), used))
const release_metadata_t g_release_meta = {
    .magic           = RELEASE_META_MAGIC,
    .build_timestamp = (uint32_t)SOURCE_DATE_EPOCH,
    .git_hash        = {0xa1, 0xb2, 0xc3, 0xd4, 0xe5, 0xf6, 0x07, 0x18, 
                        0x29, 0x3a, 0x4b, 0x5c, 0x6d, 0x7e, 0x8f, 0x90, 
                        0x12, 0x34, 0x56, 0x78},
    .toolchain_hash  = {0x3f, 0xbc, 0x63, 0x21, 0x67, 0x42, 0x4a, 0x6d},
    .firmware_crc32  = 0x9B8C7D6EU,
    .reserved        = 0U
};

bool release_metadata_is_valid(const release_metadata_t *meta) {
    if (meta == NULL) {
        return false;
    }
    if (meta->magic != RELEASE_META_MAGIC) {
        return false;
    }
    /* Перевірка наявності валідної детермінованої мітки часу */
    if (meta->build_timestamp == 0U) {
        return false;
    }
    return true;
}
