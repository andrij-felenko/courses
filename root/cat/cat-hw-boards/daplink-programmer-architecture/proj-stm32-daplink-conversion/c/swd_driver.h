#ifndef SWD_DRIVER_H
#define SWD_DRIVER_H

#include <stdint.h>
#include <stdbool.h>

/**
 * @file swd_driver.h
 * @brief Заголовний файл драйвера SWD з оголошеннями функцій програмно-апаратного
 *        формування сигналів SWCLK та SWDIO для підключення до ARM Cortex-M.
 */

/* Коди відповідей ACK протоколу SWD */
#define SWD_ACK_OK      0x01U
#define SWD_ACK_WAIT    0x02U
#define SWD_ACK_FAULT   0x04U
#define SWD_ACK_PARITY  0x08U

/* Типи запитів шини SWD */
#define SWD_REQ_AP      (1U << 0)
#define SWD_REQ_DP      (0U << 0)
#define SWD_REQ_READ    (1U << 1)
#define SWD_REQ_WRITE   (0U << 1)

/* Адреси регістрів Debug Port (DP) */
#define DP_REG_IDCODE   0x00U
#define DP_REG_ABORT    0x00U
#define DP_REG_CTRL_STAT 0x04U
#define DP_REG_SELECT   0x08U
#define DP_REG_RDBUFF   0x0CU

/**
 * @brief Ініціалізація фізичних ліній SWD (SWCLK, SWDIO, nRESET).
 */
void swd_init(void);

/**
 * @brief Генерація одного тактового імпульсу SWCLK із записом біта на SWDIO.
 * 
 * @param bit Значення біта (0 або 1).
 */
void swd_write_bit(uint8_t bit);

/**
 * @brief Генерація одного тактового імпульсу SWCLK із зчитуванням біта з SWDIO.
 * 
 * @return Зчитане значення біта (0 або 1).
 */
uint8_t swd_read_bit(void);

/**
 * @brief Зміна напрямку лінії SWDIO (Turnaround phase).
 * 
 * @param to_input true для перемикання на вхід, false для перемикання на вихід.
 */
void swd_turnaround(bool to_input);

/**
 * @brief Передача послідовності скидання лінії SWD (Line Reset: 50+ тактів High).
 */
void swd_line_reset(void);

/**
 * @brief Базова транзакція читання/запису регістрів через SWD.
 * 
 * @param request Запит формату SWD (AP/DP, Read/Write, Адреса).
 * @param data Вказівник на 32-бітний буфер даних.
 * @return Код відповіді ACK (SWD_ACK_OK, SWD_ACK_WAIT, SWD_ACK_FAULT).
 */
uint8_t swd_transfer(uint8_t request, uint32_t *data);

/**
 * @brief Зчитування регістру Debug Port (DP).
 * 
 * @param reg_addr Адреса регістру DP (DP_REG_IDCODE, DP_REG_CTRL_STAT тощо).
 * @param val Вказівник для збереження прочитаного значення.
 * @return true при успішному зчитуванні, false при помилці.
 */
bool swd_read_dp(uint8_t reg_addr, uint32_t *val);

/**
 * @brief Запис у регістр Debug Port (DP).
 * 
 * @param reg_addr Адреса регістру DP.
 * @param val Значення для запису.
 * @return true при успішному записі, false при помилці.
 */
bool swd_write_dp(uint8_t reg_addr, uint32_t val);

/**
 * @brief Зчитування регістру Access Port (AP).
 * 
 * @param ap_addr Адреса регістру AP.
 * @param val Вказівник для збереження значення.
 * @return true при успіху, false при помилці.
 */
bool swd_read_ap(uint32_t ap_addr, uint32_t *val);

/**
 * @brief Запис у регістр Access Port (AP).
 * 
 * @param ap_addr Адреса регістру AP.
 * @param val Значення для запису.
 * @return true при успіху, false при помилці.
 */
bool swd_write_ap(uint32_t ap_addr, uint32_t val);

#endif /* SWD_DRIVER_H */
