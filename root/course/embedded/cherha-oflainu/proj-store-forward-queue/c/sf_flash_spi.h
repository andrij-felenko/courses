/* sf_flash_spi.h — драйвер SPI NOR (сімейство W25Qxx / MX25Lxx).
 *
 * Драйвер бере на себе три речі, які черзі бачити не треба:
 *  - розбиття запису по сторінках 256 байтів (мікросхема НЕ вміє
 *    програмувати через межу сторінки — адреса просто загортається
 *    на початок тієї самої сторінки, і кінець запису затирає початок);
 *  - дозвіл на запис (WREN) перед кожним програмуванням і стиранням;
 *  - очікування, поки зніметься біт BUSY, з паспортним таймаутом.
 */
#ifndef SF_FLASH_SPI_H
#define SF_FLASH_SPI_H

#include <stdbool.h>
#include <stdint.h>

#include "sf_flash.h"

/* Порт платформи: три лінії SPI й годинник. Реалізація на конкретному
 * мікроконтролері — це три виклики HAL, і вони тут ні до чого. */
typedef struct {
    void (*select)(void *ctx);   /* CS -> 0 */
    void (*deselect)(void *ctx); /* CS -> 1 */
    /* Повний дуплекс: tx або rx можуть бути NULL (тоді в лінію йдуть 0xFF
     * або прийняте відкидається). false — апаратна помилка шини. */
    bool (*transfer)(void *ctx, const uint8_t *tx, uint8_t *rx, uint32_t len);
    uint32_t (*now_ms)(void *ctx);
    void *ctx;
} sf_spi_port_t;

typedef struct {
    sf_spi_port_t port;
    uint32_t      capacity;
    uint8_t       jedec_id[3];
} sf_flash_spi_t;

/* Читає JEDEC ID, звіряє з очікуваним обсягом і заповнює dev.
 * false — мікросхема не відповіла або відповіла чужим ідентифікатором. */
bool sf_flash_spi_init(sf_flash_spi_t *fl, const sf_spi_port_t *port,
                       uint32_t capacity, sf_flash_dev_t *dev);

#endif /* SF_FLASH_SPI_H */
