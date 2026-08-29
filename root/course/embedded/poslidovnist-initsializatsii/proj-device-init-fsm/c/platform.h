#ifndef PLATFORM_H
#define PLATFORM_H

#include <stdint.h>

/* Контракт плати (BSP), на який спирається автомат ініціалізації.
   На залізі це SysTick і периферія I2C; на стенді — модель у sim_device.c.
   Драйвер не знає, що саме під ним, і тому однаково тестується й там, і там. */

typedef enum {
    BUS_OK = 0,
    BUS_ERR_NACK,    /* ведений не підтвердив адресу або байт */
    BUS_ERR_TIMEOUT  /* лінія зайнята, START фізично не сформувався */
} bus_status_t;

/* Вільний лічильник мілісекунд. Переповнюється раз на ~49.7 доби —
   усі порівняння в драйвері зроблено різницею беззнакових, тож це безпечно. */
uint32_t platform_get_millis(void);

bus_status_t platform_i2c_write(uint8_t dev_addr, uint8_t reg, uint8_t val);
bus_status_t platform_i2c_read(uint8_t dev_addr, uint8_t reg, uint8_t *val);

/* Генерація 9 тактів SCL: звільняє SDA, затиснуту веденим посеред байта. */
void platform_bus_recover(void);

/* Переведення системи в безпечний стан: знеструмити виконавчі механізми,
   підняти прапорець відмови назовні. */
void platform_notify_fault(const char *reason);

#endif /* PLATFORM_H */
