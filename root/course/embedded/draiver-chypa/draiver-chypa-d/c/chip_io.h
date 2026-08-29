/* chip_io.h — надійний транспорт: повторні спроби й квантовані тайм-аути.
 *
 * Прошарок між Рівнем 1 (голі функції платформи) і Рівнем 2 (регістрова
 * логіка). Саме тут одиничний імпульс завади перетворюється на непомітну
 * затримку, а несправність — на чесний код помилки, а не на зависання.
 */
#ifndef CHIP_IO_H
#define CHIP_IO_H

#include <stdint.h>

#include "chip_dev.h"
#include "chip_status.h"

/* Транзакція читання/запису з повторами: до dev->max_retries додаткових
 * спроб із паузою, що подвоюється (1, 2, 4 мс). Вичерпали — CHIP_ERR_COMM. */
chip_status_t chip_io_read(chip_dev_t *dev, uint8_t reg, uint8_t *data, uint16_t len);
chip_status_t chip_io_write(chip_dev_t *dev, uint8_t reg, const uint8_t *data, uint16_t len);

/* Зручні обгортки для однобайтових регістрів. */
chip_status_t chip_io_read_byte(chip_dev_t *dev, uint8_t reg, uint8_t *value);
chip_status_t chip_io_write_byte(chip_dev_t *dev, uint8_t reg, uint8_t value);

/* Квантоване очікування прапорця: замість while(!flag); — цикл із кроком
 * poll_interval_ms і жорсткою стелею timeout_ms.
 *   CHIP_OK          — біти маски виставилися;
 *   CHIP_ERR_TIMEOUT — не дочекалися;
 *   CHIP_ERR_COMM    — шина не відповідає (помилку не ковтаємо).
 */
chip_status_t chip_io_wait_flag(chip_dev_t *dev, uint8_t reg, uint8_t mask,
                                uint32_t timeout_ms, uint32_t poll_interval_ms);

#endif /* CHIP_IO_H */
