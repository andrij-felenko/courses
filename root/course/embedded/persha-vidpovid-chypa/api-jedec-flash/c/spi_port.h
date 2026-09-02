#ifndef SPI_PORT_H
#define SPI_PORT_H

#include <stddef.h>
#include <stdint.h>

/* Контракт шини, якого драйверу ідентифікації досить. Під ним може стояти
   периферія мікроконтролера або симулятор кристала з цієї теки — драйвер
   різниці не бачить і бачити не мусить. */
typedef struct spi_port {
    /* CS вниз / CS вгору: межі однієї транзакції. */
    void     (*select)(struct spi_port *self);
    void     (*release)(struct spi_port *self);

    /* Повний дуплекс на len тактів SCK.
       tx == NULL — женемо 0x00 (читання), rx == NULL — відповідь відкидаємо. */
    void     (*transfer)(struct spi_port *self, const uint8_t *tx, uint8_t *rx, size_t len);

    /* Передача по чотирьох лініях даних. Потрібна рівно для одного:
       вивести кристал із режиму QPI, де однолінійних команд він не чує. */
    void     (*quad_write)(struct spi_port *self, const uint8_t *tx, size_t len);

    /* Ставить частоту й повертає ту, що реально вийшла після цілочисельного
       дільника: попросиш 20 МГц — дістанеш 20, попросиш 30 — може вийти 26.7. */
    uint32_t (*set_clock_hz)(struct spi_port *self, uint32_t hz);
    uint32_t (*clock_hz)(struct spi_port *self);

    /* Лічильник мілісекунд для тайм-аутів очікування. */
    uint32_t (*millis)(struct spi_port *self);
} spi_port_t;

/* Одна транзакція: CS вниз, командні байти по MOSI, потім читання відповіді
   з MISO, CS вгору. Розривати CS між командою й відповіддю не можна — чип
   скине внутрішній автомат і забуде опкод. */
static inline void spi_command(spi_port_t *port,
                               const uint8_t *cmd, size_t cmd_len,
                               uint8_t *rsp, size_t rsp_len)
{
    port->select(port);
    if (cmd_len > 0) {
        port->transfer(port, cmd, NULL, cmd_len);
    }
    if (rsp_len > 0) {
        port->transfer(port, NULL, rsp, rsp_len);
    }
    port->release(port);
}

#endif /* SPI_PORT_H */
