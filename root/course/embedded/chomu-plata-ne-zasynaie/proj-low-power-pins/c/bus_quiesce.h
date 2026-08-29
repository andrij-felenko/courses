/* Зупинка послідовних інтерфейсів перед сном.
 *
 * Модуль відповідає лише на одне питання: чи можна вже гасити тактування й
 * живлення, не обірвавши кадр і не лишивши шину заклиненою.
 */
#ifndef BUS_QUIESCE_H
#define BUS_QUIESCE_H

#include "mcu.h"

typedef enum {
    BUS_OK = 0,
    BUS_ERR_UART_TC,   /* останній кадр не встиг вийти на лінію */
    BUS_ERR_SPI_BUSY,  /* зсувний регістр SPI досі крутить біти */
    BUS_ERR_I2C_BUSY,  /* транзакція на шині не завершилася */
    BUS_ERR_I2C_STUCK  /* ведений тримає SDA у нулі й після відновлення */
} bus_status_t;

const char *bus_status_str(bus_status_t st);

/* Чекає TC (передача завершена), а не TXE (буфер вільний), і аж тоді знімає UE. */
bus_status_t bus_quiesce_uart(usart_t *u, uint32_t timeout_us);

/* Чекає спустошення черги передачі FTLVL і зняття BSY, тоді знімає SPE. */
bus_status_t bus_quiesce_spi(spi_t *s, uint32_t timeout_us);

/* Чекає зняття BUSY, тоді знімає PE — це відпускає SDA і SCL у Hi-Z. */
bus_status_t bus_quiesce_i2c(i2c_t *i, uint32_t timeout_us);

/* Усі три шини плати одним викликом; повертає першу ж помилку. */
bus_status_t bus_quiesce_all(uint32_t timeout_us);

/* Розклинення I2C: дев'ять тактів SCL руками плюс умова STOP.
 * Потрібне, коли ведений знеструмили посеред байта і він лишився тримати SDA. */
bus_status_t bus_recover_i2c(void);

#endif /* BUS_QUIESCE_H */
