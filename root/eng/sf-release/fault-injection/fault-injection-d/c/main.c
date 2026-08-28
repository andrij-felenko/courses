#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SLOT_A_ADDR   0x08020000U
#define SLOT_B_ADDR   0x080A0000U
#define SLOT_SIZE     0x00080000U  /* 512 КБ */

typedef struct {
    uint32_t magic;           /* 0x544F4F42 ("BOOT") */
    uint32_t version_raw;
    uint32_t image_size;
    uint32_t expected_crc32;
    uint32_t flags;           /* 0x01: PENDING, 0x02: CONFIRMED */
} __attribute__((packed)) image_header_t;

/* Обчислення контрольної суми CRC32 над областю Flash */
static uint32_t flash_crc32(uint32_t start_addr, uint32_t length) {
    uint32_t crc = 0xFFFFFFFFU;
    const uint8_t *p = (const uint8_t *)start_addr;
    for (uint32_t i = 0; i < length; ++i) {
        crc ^= p[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & -(crc & 1U));
        }
    }
    return ~crc;
}

/* Атомарна валідація образу перед передачею керування */
uint32_t bootloader_select_valid_slot(void) {
    const image_header_t *hdr_b = (const image_header_t *)SLOT_B_ADDR;
    
    /* 1. Перевіряємо заголовок цільового слота B (оновленого) */
    if (hdr_b->magic == 0x544F4F42 && hdr_b->image_size <= (SLOT_SIZE - sizeof(image_header_t))) {
        /* Обчислюємо CRC32 самого тіла прошивки */
        uint32_t calc_crc = flash_crc32(SLOT_B_ADDR + sizeof(image_header_t), hdr_b->image_size);
        
        if (calc_crc == hdr_b->expected_crc32) {
            /* Новий образ цілісний — стартуємо Слот B */
            return SLOT_B_ADDR + sizeof(image_header_t);
        }
    }

    /* 2. Якщо Слот B пошкоджено обривом живлення — безпечний відкат на стабільний Слот A */
    const image_header_t *hdr_a = (const image_header_t *)SLOT_A_ADDR;
    if (hdr_a->magic == 0x544F4F42) {
        uint32_t calc_crc_a = flash_crc32(SLOT_A_ADDR + sizeof(image_header_t), hdr_a->image_size);
        if (calc_crc_a == hdr_a->expected_crc32) {
            return SLOT_A_ADDR + sizeof(image_header_t);
        }
    }

    /* Обидва слоти невалідні — фатальна зупинка */
    return 0;
}
