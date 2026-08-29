/* Живлення датчиків: програмний standby по шині, силовий ключ, розряд ємностей.
 *
 * Порядок тут не косметичний. Спершу датчик просять заснути командою, потім
 * зупиняють шину, і лише тоді розмикають ключ — інакше ведений лишається з
 * недоказаним байтом і тримає SDA.
 */
#ifndef SENSOR_POWER_H
#define SENSOR_POWER_H

#include "bus_quiesce.h"

/* Силовий ключ P-MOSFET на PB12: нуль відкриває, одиниця закриває. */
#define RAIL_SWITCH_PORT GPIOB
#define RAIL_SWITCH_PIN  12U

typedef enum {
    RAIL_OK = 0,
    RAIL_ERR_I2C_NACK,    /* датчик не підтвердив адресу або байт */
    RAIL_ERR_I2C_TIMEOUT, /* модуль не дійшов до наступного стану */
    RAIL_ERR_BUS,         /* шину не вдалося зупинити чисто */
    RAIL_ERR_ID           /* після подання живлення на шині не той датчик */
} rail_status_t;

const char *rail_status_str(rail_status_t st);

/* Обмін по I2C. Адреса семибітна, як у даташиті. */
rail_status_t i2c_write_reg(uint8_t addr7, uint8_t reg, uint8_t value);
rail_status_t i2c_read_regs(uint8_t addr7, uint8_t reg, uint8_t *dst, uint8_t len);

/* Повний вимикальний хід: standby датчикам, зупинка шин, розмикання ключа,
 * витримка на розряд блокувальних ємностей. */
rail_status_t sensor_rail_shutdown(void);

/* Зворотний хід: ключ, час наростання й старту датчиків, перевірка ідентифікатора,
 * повторна конфігурація вимірювання. */
rail_status_t sensor_rail_power_up(void);

/* Одне вимірювання температури барометра — щоб цикл сну мав що робити. */
rail_status_t sensor_read_temperature_raw(int32_t *raw);

#endif /* SENSOR_POWER_H */
