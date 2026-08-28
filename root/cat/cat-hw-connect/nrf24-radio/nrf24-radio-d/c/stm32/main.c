// STM32 HAL: драйвера nRF24 в HAL теж нема — ті самі регістри по HAL_SPI_Transmit.
// CSN смикаємо руками (HAL його не веде), CE — звичайний вихід.
#include "stm32f4xx_hal.h"
#include <string.h>

#define CSN_PORT GPIOA
#define CSN_PIN  GPIO_PIN_4
#define CE_PORT  GPIOB
#define CE_PIN   GPIO_PIN_0

extern SPI_HandleTypeDef hspi1;           // 8 МГц, режим 0, старшим бітом уперед

static void nrf_cmd(uint8_t *buf, uint16_t n) {
    HAL_GPIO_WritePin(CSN_PORT, CSN_PIN, GPIO_PIN_RESET);   // CSN активний у нулі
    HAL_SPI_Transmit(&hspi1, buf, n, HAL_MAX_DELAY);
    HAL_GPIO_WritePin(CSN_PORT, CSN_PIN, GPIO_PIN_SET);
}

static void nrf_wr(uint8_t reg, const uint8_t *v, uint16_t n) {   // W_REGISTER = 0x20|reg
    uint8_t tx[6] = { (uint8_t)(0x20 | reg) };
    memcpy(tx + 1, v, n);
    nrf_cmd(tx, n + 1);
}

void nrf_begin(void) {                    // SPI1 і виводи вже підняті MX_*_Init()
    HAL_GPIO_WritePin(CE_PORT, CE_PIN, GPIO_PIN_RESET);     // радіо поки спить
    HAL_GPIO_WritePin(CSN_PORT, CSN_PIN, GPIO_PIN_SET);

    uint8_t ch = 76, rf = 0x22, cfg = 0x0A;   // канал 76 · 250 кбіт/с · потужність LOW
    const uint8_t addr[5] = { 'n','o','d','e','1' };
    nrf_wr(0x05, &ch, 1);                 // RF_CH — має збігатися з іншим кінцем
    nrf_wr(0x06, &rf, 1);                 // RF_SETUP — швидкість і потужність
    nrf_wr(0x10, addr, 5);                // TX_ADDR
    nrf_wr(0x0A, addr, 5);                // RX_ADDR_P0 — інакше не приймемо авто-ACK
    nrf_wr(0x00, &cfg, 1);                // CONFIG: PWR_UP + CRC, режим передавача
}

void nrf_send(const void *data, uint16_t n) {   // n ≤ 32
    uint8_t tx[33] = { 0xA0 };            // W_TX_PAYLOAD
    memcpy(tx + 1, data, n);
    nrf_cmd(tx, n + 1);

    HAL_GPIO_WritePin(CE_PORT, CE_PIN, GPIO_PIN_SET);       // імпульс CE — «в ефір»
    HAL_Delay(1);                         // треба ≥10 мкс; 1 мс — груба, зате робоча пауза
    HAL_GPIO_WritePin(CE_PORT, CE_PIN, GPIO_PIN_RESET);
    // підсумок — у регістрі STATUS: TX_DS «підтверджено», MAX_RT «спроби вичерпано»
}
