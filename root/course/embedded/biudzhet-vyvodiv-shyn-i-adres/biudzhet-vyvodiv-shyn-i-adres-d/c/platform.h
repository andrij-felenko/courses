#ifndef PLATFORM_H
#define PLATFORM_H

#include <stdbool.h>
#include <stdint.h>

/* Результат шинної операції. Платформний шар мусить розрізняти NACK
   (пристрою нема або він зайнятий) і аварію самої шини: реакція різна —
   на NACK пробуємо ще раз, на аварію смикаємо апаратне скидання. */
typedef enum {
    IO_OK = 0,
    IO_ERR_ARG,      /* некоректний аргумент: номер каналу, довжина буфера */
    IO_ERR_NACK,     /* ведений не підтвердив адресу або байт даних */
    IO_ERR_BUS,      /* втрата арбітражу, SDA/SCL притиснуті в нуль */
    IO_ERR_TIMEOUT
} io_status_t;

/* Ознака «вивід не заведений на плату». */
#define PIN_NONE 0xFFu

/* --- Контракт драйвера I2C конкретного мікроконтролера --- */

io_status_t i2c_write(uint8_t dev, const uint8_t *data, uint8_t len);
io_status_t i2c_read(uint8_t dev, uint8_t *buf, uint8_t len);

/* Запис адреси регістра, повторний старт, читання — типовий доступ до
   регістрів веденого чипа однією неподільною транзакцією. */
io_status_t i2c_write_read(uint8_t dev, const uint8_t *out, uint8_t out_len,
                           uint8_t *in, uint8_t in_len);

/* --- Контракт драйвера SPI ---
   tx == NULL: на MOSI подаються одиниці; rx == NULL: прийняте відкидається. */
io_status_t spi_transfer(const uint8_t *tx, uint8_t *rx, uint16_t len);

/* --- Контракт дискретних виводів --- */

void gpio_write(uint8_t pin, bool high);
bool gpio_read(uint8_t pin);
void delay_us(uint32_t us);

#endif /* PLATFORM_H */
