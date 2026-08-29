/* i2c_rescue.h — нагляд за зовнішньою шиною та її розчепірювання.
 *
 * Класичне польове зависання: раб посеред віддавання байта побачив на
 * живленні просадку й перезапустився, а майстер — ні. Раб тримає SDA внизу,
 * чекаючи на такти, яких уже ніхто не дасть; майстер бачить зайняту шину
 * й не може навіть почати. Периферія сама з цього не вийде — виводить
 * ручне тактування ніжками.
 */
#ifndef I2C_RESCUE_H
#define I2C_RESCUE_H

#include <stdbool.h>
#include <stdint.h>

typedef enum {
    BUS_HEALTH_OK = 0,
    BUS_HEALTH_SILENT,    /* раб не відповідає, але лінії вільні */
    BUS_HEALTH_STUCK,     /* лінію тримають унизу: класичне зависання */
    BUS_HEALTH_RECOVERED, /* тримали, розчепірили, зараз відповідає */
    BUS_HEALTH_DEAD       /* порятунок не допоміг */
} bus_health_t;

typedef struct {
    uint8_t address;
    uint16_t fail_streak;    /* скільки перевірок поспіль без відповіді */
    uint16_t recover_streak; /* скільки порятунків поспіль не дали результату */
    uint32_t recover_total;
} i2c_bus_t;

void i2c_bus_init(i2c_bus_t *bus, uint8_t address);

/* Перевіряє шину й, коли треба, сама її рятує. Повертає підсумок спроби. */
bus_health_t i2c_bus_check(i2c_bus_t *bus);

/* Читання з обліком: невдача веде облік так само, як і перевірка. */
bool i2c_bus_read(i2c_bus_t *bus, uint8_t reg, uint8_t *buf, uint8_t len);

#endif /* I2C_RESCUE_H */
