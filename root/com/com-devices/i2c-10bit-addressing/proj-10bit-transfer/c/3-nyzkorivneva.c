#include "stm32f4xx_ll_i2c.h"
#include "stm32f4xx_ll_bus.h"

/* Низькорівневий запис одного байта в 10-бітний пристрій через прямий огляд регістрів */
int LL_I2C1_Write10Bit_Polling(I2C_TypeDef *I2Cx, uint16_t addr10, uint8_t data) {
    /* 1. Генерація сигналу START */
    LL_I2C_GenerateStartCondition(I2Cx);
    while (!LL_I2C_IsActiveFlag_SB(I2Cx)) {
        /* Очікування встановлення прапорця Start Bit */
    }

    /* 2. Відправка 1-го байта заголовка: 1111 0 A9 A8 0 (напрямок запису) */
    uint8_t header1 = (uint8_t)(0xF0 | (((addr10 >> 8) & 0x03) << 1));
    LL_I2C_TransmitData8(I2Cx, header1);

    /* 3. Очікування передачі 1-го байта (прапорець ADD10 у регістрі SR1) */
    while (!LL_I2C_IsActiveFlag_ADD10(I2Cx)) {
        if (LL_I2C_IsActiveFlag_AF(I2Cx)) {
            LL_I2C_ClearFlag_AF(I2Cx);
            LL_I2C_GenerateStopCondition(I2Cx);
            return -1; /* Отримано NACK на 1-му байті */
        }
    }

    /* 4. Відправка 2-го байта адреси (молодші 8 бітів A7..A0) */
    uint8_t header2 = (uint8_t)(addr10 & 0xFF);
    LL_I2C_TransmitData8(I2Cx, header2);

    /* 5. Очікування повного зіставлення адреси (прапорець ADDR) */
    while (!LL_I2C_IsActiveFlag_ADDR(I2Cx)) {
        if (LL_I2C_IsActiveFlag_AF(I2Cx)) {
            LL_I2C_ClearFlag_AF(I2Cx);
            LL_I2C_GenerateStopCondition(I2Cx);
            return -1; /* Отримано NACK на 2-му байті */
        }
    }

    /* Очищення прапорця ADDR читанням SR1, потім SR2 */
    LL_I2C_ClearFlag_ADDR(I2Cx);

    /* 6. Передача байта даних */
    while (!LL_I2C_IsActiveFlag_TXE(I2Cx)) {}
    LL_I2C_TransmitData8(I2Cx, data);

    /* 7. Очікування завершення передачі байта (Byte Transfer Finished) */
    while (!LL_I2C_IsActiveFlag_BTF(I2Cx)) {}

    /* 8. Генерація сигналу STOP */
    LL_I2C_GenerateStopCondition(I2Cx);
    return 0;
}
