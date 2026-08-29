#ifndef MANIFEST_H
#define MANIFEST_H

#include <stddef.h>
#include <stdint.h>

#include "boot_status.h"

#define MANIFEST_MAGIC        0x5346574DU  /* "SFWM", little-endian у Flash */
#define BOOT_KEY_SLOTS        4U
#define SHA256_SIZE           32U
#define PUBKEY_SIZE           64U          /* ECDSA P-256: координати X||Y */
#define SIGNATURE_SIZE        64U          /* ECDSA P-256: r||s */

/*
 * Заголовок образу лежить у Flash першими байтами розділу, тому структуру
 * упаковано: розкладка полів мусить збігатися з байтами на носії один в один.
 */
typedef struct {
    uint32_t magic;             /* 0x00: MANIFEST_MAGIC */
    uint32_t header_crc;        /* 0x04: CRC-32 усіх байтів заголовка ПІСЛЯ цього поля */
    uint32_t payload_length;    /* 0x08: довжина тіла прошивки за заголовком */
    uint32_t load_address;      /* 0x0C: адреса, з якої стартує образ */
    uint32_t security_version;  /* 0x10: версія безпеки для анти-відкату */
    uint8_t  key_slot_index;    /* 0x14: яким зі слотів 0..3 підписано */
    uint8_t  reserved[3];       /* 0x15: вирівнювання, мусить бути нулями */
    uint8_t  public_key[PUBKEY_SIZE];   /* 0x18: відкритий ключ підписанта */
    uint8_t  signature[SIGNATURE_SIZE]; /* 0x58: підпис заголовка разом із тілом */
} __attribute__((packed)) firmware_manifest_t;

#define MANIFEST_SIZE         ((size_t)152)  /* 0x98 */
#define MANIFEST_CRC_OFFSET   ((size_t)8)    /* з чого починається покритий CRC шматок */
#define MANIFEST_SIGNED_SIZE  ((size_t)88)   /* заголовок без поля signature */

/*
 * Читає й перевіряє заголовок розділу: розмір, магічне число, CRC-32,
 * діапазон індексу слота і те, що тіло вміщується у розділ.
 * Повертає BOOT_ERR_MAGIC на будь-яке пошкодження самого заголовка.
 */
boot_status_t manifest_parse(const uint8_t *slot_base,
                             uint32_t slot_size,
                             firmware_manifest_t *out);

/* Тіло прошивки починається одразу за заголовком. */
static inline const uint8_t *manifest_payload(const uint8_t *slot_base)
{
    return slot_base + MANIFEST_SIZE;
}

#endif /* MANIFEST_H */
