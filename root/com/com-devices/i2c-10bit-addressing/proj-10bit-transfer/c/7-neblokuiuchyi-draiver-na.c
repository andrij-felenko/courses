#include "stm32f4xx_ll_i2c.h"
#include <stdint.h>

typedef enum {
    I2C_STATE_IDLE = 0,
    I2C_STATE_HEADER1,
    I2C_STATE_HEADER2,
    I2C_STATE_DATA_TX,
    I2C_STATE_DATA_RX,
    I2C_STATE_COMPLETE
} i2c_async_state_t;

typedef struct {
    uint16_t addr10;
    uint8_t *tx_buf;
    uint16_t tx_len;
    uint16_t tx_idx;
    volatile i2c_async_state_t state;
} i2c_async_transfer_t;

static i2c_async_transfer_t g_transfer;

void I2C1_EV_IRQHandler_Custom(I2C_TypeDef *I2Cx) {
    if (LL_I2C_IsActiveFlag_SB(I2Cx)) {
        /* Генерація 1-го байта заголовка */
        uint8_t h1 = (uint8_t)(0xF0 | (((g_transfer.addr10 >> 8) & 0x03) << 1));
        LL_I2C_TransmitData8(I2Cx, h1);
        g_transfer.state = I2C_STATE_HEADER1;
    } else if (LL_I2C_IsActiveFlag_ADD10(I2Cx)) {
        /* Відправка 2-го байта адреси */
        uint8_t h2 = (uint8_t)(g_transfer.addr10 & 0xFF);
        LL_I2C_TransmitData8(I2Cx, h2);
        g_transfer.state = I2C_STATE_HEADER2;
    } else if (LL_I2C_IsActiveFlag_ADDR(I2Cx)) {
        LL_I2C_ClearFlag_ADDR(I2Cx);
        g_transfer.state = I2C_STATE_DATA_TX;
    } else if (LL_I2C_IsActiveFlag_TXE(I2Cx) && g_transfer.state == I2C_STATE_DATA_TX) {
        if (g_transfer.tx_idx < g_transfer.tx_len) {
            LL_I2C_TransmitData8(I2Cx, g_transfer.tx_buf[g_transfer.tx_idx++]);
        } else {
            LL_I2C_GenerateStopCondition(I2Cx);
            LL_I2C_DisableIT_EVT(I2Cx);
            LL_I2C_DisableIT_BUF(I2Cx);
            g_transfer.state = I2C_STATE_COMPLETE;
        }
    }
}
