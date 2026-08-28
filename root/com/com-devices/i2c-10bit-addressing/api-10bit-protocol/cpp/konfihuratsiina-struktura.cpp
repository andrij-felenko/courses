#include <cstdint>

struct Stm32I2cConfig {
    uint32_t clockSpeed{100000};       // Тактова частота шини (100000 для Standard або 400000 для Fast)
    uint32_t dutyCycle{2};             // Коефіцієнт заповнення сигналу SCL у швидкому режимі
    uint32_t ownAddress1{0};           // Власна 7- або 10-бітна адреса мікроконтролера в режимі веденого
    uint32_t addressingMode{0x0000C000};// I2C_ADDRESSINGMODE_10BIT
    uint32_t dualAddressMode{0};       // Дозвіл використання другої власної адреси
    uint32_t ownAddress2{0};           // Друга власна адреса
    uint32_t generalCallMode{0};       // Реакція на адресу загального виклику
    uint32_t noStretchMode{0};         // Заборона розтягування тактового сигналу
};
