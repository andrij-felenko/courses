#ifndef DEVICES_H
#define DEVICES_H

/* Драйвери трьох зовнішніх чипів вузла: BME280 і DS3231 на I2C,
 * NOR Flash W25Q128JV на SPI1. */

#include <stdint.h>
#include <stdbool.h>

/* ── BME280 ──────────────────────────────────────────────────────────────── */

bool bme280_init(void);            /* перевірка ID, читання калібрувань, режим */

/* Вимірювання ділиться надвоє: запуск і забір. Між ними ~10 мс, і головний
 * цикл ці 10 мс займається чим завгодно, а не чекає в while. */
bool bme280_start(void);
bool bme280_ready(void);
bool bme280_fetch(int32_t *temp_c100, uint32_t *press_pa100, uint32_t *hum_rh1024);

/* ── DS3231 ──────────────────────────────────────────────────────────────── */

bool ds3231_init(void);            /* меандр 1 Гц на INT/SQW */
bool ds3231_time(uint32_t *unix_time, bool *clock_valid);

/* ── W25Q128JV ───────────────────────────────────────────────────────────── */

void flash_init(void);
bool flash_present(void);          /* JEDEC ID 0xEF 0x40 0x18 */
bool flash_read(uint32_t addr, uint8_t *dst, uint32_t len);
bool flash_busy(void);             /* біт BUSY регістра стану 1 */

/* Обидві операції запуску не чекають завершення: керує ним автомат логера. */
bool flash_page_program_start(uint32_t addr, const uint8_t *src, uint16_t len);
bool flash_sector_erase_start(uint32_t addr);

/* Після зняття BUSY: WEL мусить бути скинутий апаратно — інакше команда
 * не виконалася, і це єдина чесна ознака помилки запису в цьому чипі. */
bool flash_last_op_ok(void);

#endif /* DEVICES_H */
