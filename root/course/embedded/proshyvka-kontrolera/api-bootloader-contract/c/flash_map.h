#ifndef FLASH_MAP_H
#define FLASH_MAP_H

#include <stddef.h>
#include <stdint.h>

#include "dfu_proto.h"

/* Карта Flash STM32F405: 4*16K + 1*64K + 7*128K = 1 МБ. */
#define FLASH_BASE_ADDR  0x08000000u
#define FLASH_TOTAL_SIZE (1024u * 1024u)
/* Перші два сектори по 16 КБ займає сам завантажувач. */
#define FLASH_APP_BASE   0x08008000u

/* Прапорці доступу для рядка карти пам'яті DfuSe. */
#define FLASH_ACC_READ  0x1u
#define FLASH_ACC_ERASE 0x2u
#define FLASH_ACC_WRITE 0x4u

typedef struct {
    uint32_t address;
    uint32_t size;
    uint8_t  index;  /* Номер сектора для поля SNB регістра FLASH_CR */
    uint8_t  access; /* Комбінація FLASH_ACC_* */
} flash_sector_t;

const flash_sector_t *flash_map_sector_at(uint32_t address);
int      flash_map_is_app_range(uint32_t address, size_t length);
uint32_t flash_map_erase_timeout_ms(const flash_sector_t *sector);
uint32_t flash_map_app_erase_timeout_ms(void);

/* Рядок вигляду "@Internal Flash  /0x08000000/02*016Ka,02*016Kg,..." */
size_t flash_map_layout_string(char *out, size_t cap);
/* Той самий рядок, загорнутий у USB String Descriptor (UTF-16LE). */
size_t flash_map_layout_descriptor(uint8_t *out, size_t cap);

dfu_status_t flash_erase_sector(uint32_t address);
dfu_status_t flash_erase_application(void);
dfu_status_t flash_program(uint32_t address, const uint8_t *data, size_t length);
const uint8_t *flash_read(uint32_t address, size_t length);
int flash_app_image_valid(void);

#endif /* FLASH_MAP_H */
