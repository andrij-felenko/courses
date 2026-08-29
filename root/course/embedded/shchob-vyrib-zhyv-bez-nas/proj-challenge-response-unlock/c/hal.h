#ifndef EOLBOOT_HAL_H
#define EOLBOOT_HAL_H

/*
 * Контракт до заліза. Реалізацію дає BSP конкретної плати (вендорський SDK):
 * тут лише те, чого потребує логіка розблокування завантажувача.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define CHIP_UUID_LEN 16

/* Сховище користувацьких параметрів: Wi-Fi паролі, токени, сертифікати */
#define NVS_BASE_ADDR   0x08040000u
#define NVS_SECTOR_SIZE 4096u
#define NVS_SECTORS_NUM 8u

/* Апаратний генератор справжніх випадкових чисел */
void hal_trng_fill(uint8_t *dest, size_t len);

/* Фабричний номер кристала, зашитий на пластині заводом-виробником чіпа */
void hal_get_chip_uuid(uint8_t dest[CHIP_UUID_LEN]);

uint32_t hal_get_tick_ms(void);

/* Flash: стирання переводить біти в 0xFF, запис уміє лише 1 -> 0 */
bool hal_flash_erase_sector(uint32_t sector_addr);
bool hal_flash_write(uint32_t addr, const uint8_t *data, size_t len);
bool hal_flash_read(uint32_t addr, uint8_t *dest, size_t len);

/* Комірка eFuse статусу: перепалюється один раз і незворотно */
bool hal_efuse_read_unlocked(void);
bool hal_efuse_burn_unlocked(void);

/* Діагностичний порт (UART або USB CDC); читання неблокуюче */
bool hal_uart_read_byte(uint8_t *out);
void hal_uart_write(const uint8_t *data, size_t len);

_Noreturn void hal_reboot(void);

#endif /* EOLBOOT_HAL_H */
