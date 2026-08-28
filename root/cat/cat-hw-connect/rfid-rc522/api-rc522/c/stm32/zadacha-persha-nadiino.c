#include "stm32f4xx_hal.h"
#include <stdio.h>

extern SPI_HandleTypeDef hspi1;     // CPOL=0, CPHA=0, до 10 МГц, старшим бітом уперед

// Адресний байт MFRC522: біт 7 = 1 читання / 0 запис, біти 6..1 — номер регістра.
static void pcd_write(uint8_t reg, uint8_t v) {
    uint8_t tx[2] = { (uint8_t)((reg << 1) & 0x7E), v };
    HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_RESET);
    HAL_SPI_Transmit(&hspi1, tx, 2, HAL_MAX_DELAY);
    HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_SET);
}
static uint8_t pcd_read(uint8_t reg) {
    uint8_t tx[2] = { (uint8_t)(((reg << 1) & 0x7E) | 0x80), 0 }, rx[2];
    HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_RESET);
    HAL_SPI_TransmitReceive(&hspi1, tx, rx, 2, HAL_MAX_DELAY);
    HAL_GPIO_WritePin(CS_GPIO_Port, CS_Pin, GPIO_PIN_SET);
    return rx[1];
}

static uint8_t uid[10], uid_len, sak;

int main(void) {
    HAL_Init(); SystemClock_Config(); MX_GPIO_Init(); MX_SPI1_Init();
    HAL_GPIO_WritePin(RST_GPIO_Port, RST_Pin, GPIO_PIN_SET);   // зняти апаратний RESET
    pcd_init();                 // SoftReset (0x0F) + увімкнути антену: TxControlReg |= 0x03
    printf("Піднесіть мітку...\r\n");

    while (1) {
        // 1. REQA (0x26) — чи озветься нова мітка в полі
        if (picc_request(0x26) != HAL_OK) { HAL_Delay(50); continue; }

        // 2. антиколізія й SELECT (0x93) → UID у uid[], відповідь мітки у sak
        if (picc_select(uid, &uid_len, &sak) != HAL_OK) continue;

        // 3. UID
        printf("UID:");
        for (uint8_t i = 0; i < uid_len; i++) printf(" %02X", uid[i]);

        // 4. тип мітки — за SAK: 0x08 Classic 1K, 0x18 Classic 4K, 0x00 Ultralight/NTAG
        printf("\r\nТип: %s\r\n", picc_type_name(sak));

        // 5. HLTA (0x50 0x00 + CRC) — відпустити мітку, інакше читатимемо її без кінця
        picc_halta();
    }
}
