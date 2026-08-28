#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TARGET_TRIGGER_PIN (1U << 12)

/* Імітація запису оновленого блоку прошивки у SPI NOR Flash */
typedef struct {
    uint32_t magic;
    uint32_t seq_number;
    uint32_t crc32;
    uint8_t  payload[256];
} flash_page_payload_t;

/* Простий обчислювач апаратного або програмного CRC32 */
uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320 & -(crc & 1));
        }
    }
    return ~crc;
}

/* Функція виконання критичної транзакції оновлення */
void execute_critical_flash_update(uint32_t sector_address, uint32_t sequence_id) {
    flash_page_payload_t block;
    block.magic = 0xAA55AA55;
    block.seq_number = sequence_id;
    memset(block.payload, 0x42, sizeof(block.payload));
    block.crc32 = calculate_crc32((const uint8_t *)&block.seq_number, sizeof(block.seq_number) + sizeof(block.payload));

    /* 1. Виставляємо апаратний тригер HIGH: старт критичної зони */
    /* GPIO_TARGET->BSRR = TARGET_TRIGGER_PIN; */

    /* 2. Стирання сектора NOR Flash (типова тривалість 40-100 мс) */
    /* spi_flash_erase_sector(sector_address); */

    /* 3. Програмування сторінки даних (типова тривалість 200-400 мкс) */
    /* spi_flash_write_page(sector_address, (uint8_t*)&block, sizeof(block)); */

    /* 4. Скидаємо тригер у LOW: критична зона завершена успішно */
    /* GPIO_TARGET->BSRR = (TARGET_TRIGGER_PIN << 16); */
}
