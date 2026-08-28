#include <stdint.h>

typedef struct {
    uint32_t ClockSpeed;       /* Тактова частота шини (100000 для Standard або 400000 для Fast) */
    uint32_t DutyCycle;        /* Коефіцієнт заповнення сигналу SCL у швидкому режимі (2 або 16/9) */
    uint32_t OwnAddress1;      /* Власна 7- або 10-бітна адреса мікроконтролера в режимі веденого */
    uint32_t AddressingMode;   /* Розрядність адреси: I2C_ADDRESSINGMODE_7BIT або I2C_ADDRESSINGMODE_10BIT */
    uint32_t DualAddressMode;  /* Дозвіл використання другої власної адреси */
    uint32_t OwnAddress2;      /* Друга власна адреса (підтримує лише 7-бітний формат) */
    uint32_t GeneralCallMode;  /* Реакція на адресу загального виклику 0x00 */
    uint32_t NoStretchMode;    /* Заборона розтягування тактового сигналу (Clock Stretching) */
} I2C_InitTypeDef;
