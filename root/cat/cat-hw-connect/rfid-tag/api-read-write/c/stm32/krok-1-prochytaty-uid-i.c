#include "stm32f4xx_hal.h"
#include <stdio.h>

extern SPI_HandleTypeDef  hspi1;
extern UART_HandleTypeDef huart2;
#define CS_PORT GPIOB
#define CS_PIN  GPIO_PIN_6            // «SDA» плати — це chip-select

// УВЕСЬ платформозалежний код — оці дві функції: опустити CS і прогнати два
// байти. Адреса регістра: запис (reg << 1) & 0x7E, читання — те саме | 0x80.
static void pcd_write(uint8_t reg, uint8_t val) {
    uint8_t tx[2] = { (reg << 1) & 0x7E, val };
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_RESET);
    HAL_SPI_Transmit(&hspi1, tx, 2, HAL_MAX_DELAY);
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);
}
static uint8_t pcd_read(uint8_t reg) {
    uint8_t tx[2] = { ((reg << 1) & 0x7E) | 0x80, 0 }, rx[2];
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_RESET);
    HAL_SPI_TransmitReceive(&hspi1, tx, rx, 2, HAL_MAX_DELAY);
    HAL_GPIO_WritePin(CS_PORT, CS_PIN, GPIO_PIN_SET);
    return rx[1];
}

void rc522_init(void) {                           // те, що на Arduino робить PCD_Init()
    pcd_write(0x01, 0x0F);                        // CommandReg ← SoftReset
    HAL_Delay(50);
    pcd_write(0x2A, 0x80); pcd_write(0x2B, 0xA9); // таймер очікування відповіді мітки
    pcd_write(0x2C, 0x03); pcd_write(0x2D, 0xE8);
    pcd_write(0x15, 0x40); pcd_write(0x11, 0x3D); // 100% ASK, CRC-preset 0x6363
    pcd_write(0x14, pcd_read(0x14) | 0x03);       // TxControlReg: антена на
}

void rc522_poll(void) {                           // кличемо з головного циклу
    uint8_t uid[10], uid_len, sak, line[80];
    // picc_select — код протоколу ISO 14443A поверх pcd_write/pcd_read: він
    // однаковий скрізь, платформа міняє лише транспорт вище.
    if (picc_select(uid, &uid_len, &sak) != PICC_OK) return;
    int k = snprintf((char *)line, sizeof line, "UID (%u байт):", uid_len);
    for (uint8_t i = 0; i < uid_len; i++)         // саме uid_len, не жорсткі 4
        k += snprintf((char *)line + k, sizeof line - k, " %02X", uid[i]);
    k += snprintf((char *)line + k, sizeof line - k, "\r\nЧип: %s\r\n", picc_type_name(sak));
    HAL_UART_Transmit(&huart2, line, k, HAL_MAX_DELAY);
    picc_halt_a();
}
