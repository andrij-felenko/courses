/*
 * Публічний інтерфейс адаптера. Заголовків мікросхеми тут немає й не буде:
 * бізнес-модуль бачить непрозорий тип, шину й структуру величин SI.
 */
#ifndef SENSOR_ADAPTER_H
#define SENSOR_ADAPTER_H

#include "sys_i2c.h"

/* Непрозорий дескриптор: розмір і поля відомі лише sensor_adapter.c. */
typedef struct sensor_adapter sensor_adapter_t;

/*
 * Займає слот зі статичного пулу, прив'язує колбеки й ініціалізує чип.
 * Поки не повернуто SYS_OK, *out лишається NULL.
 */
sys_status_t sensor_adapter_acquire(sys_i2c_bus_t *bus, uint8_t i2c_addr,
                                    sensor_adapter_t **out);

/* Переводить чип у сон і повертає слот у пул. NULL допустимий. */
void sensor_adapter_release(sensor_adapter_t *adapter);

/* Одне вимірювання на вимогу. На помилці *out обнулено. */
sys_status_t sensor_adapter_read(sensor_adapter_t *adapter, sensor_data_t *out);

#endif /* SENSOR_ADAPTER_H */
