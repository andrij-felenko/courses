#include <stdio.h>
#include "sensor_driver.h"

/* Реальні функції периферії мікроконтролера */
extern sensor_status_t mcu_i2c_read(void *ctx, uint8_t reg, uint8_t *data, size_t len);
extern sensor_status_t mcu_i2c_write(void *ctx, uint8_t reg, const uint8_t *data, size_t len);
extern uint32_t mcu_get_systick_us(void);
extern sensor_status_t mcu_i2c_recover(void *ctx);

static const sensor_bus_ops_t g_i2c_ops = {
    .read = mcu_i2c_read,
    .write = mcu_i2c_write,
    .get_time_us = mcu_get_systick_us,
    .recover_bus = mcu_i2c_recover
};

void application_task_step(sensor_device_t *sensor) {
    sensor_data_t telemetry;

    switch (sensor->state) {
        case SENSOR_STATE_IDLE:
            /* Запуск періодичного заміру */
            sensor_start_measurement(sensor);
            break;

        case SENSOR_STATE_CONVERTING: {
            /* Неблокуюча перевірка готовності */
            sensor_status_t st = sensor_poll(sensor, &telemetry);
            if (st == SENSOR_OK) {
                /* Дані успішно отримані та перевірені за CRC */
                printf("T = %ld mC, P = %lu Pa\n", (long)telemetry.temperature_mdeg_c, (unsigned long)telemetry.pressure_pa);
            } else if (st == SENSOR_ERR_NOT_READY) {
                /* Конверсія ще триває: процесор обслуговує інші модулі */
            } else {
                /* Виявлено збій шини або CRC: спроба відновлення */
                if (sensor->ops && sensor->ops->recover_bus) {
                    sensor->ops->recover_bus(sensor->user_ctx);
                }
                sensor_reset_fsm(sensor);
            }
            break;
        }

        case SENSOR_STATE_DATA_READY:
            /* Перезапуск наступного циклу заміру */
            sensor_start_measurement(sensor);
            break;

        case SENSOR_STATE_ERROR:
        default:
            if (sensor->ops && sensor->ops->recover_bus) {
                sensor->ops->recover_bus(sensor->user_ctx);
            }
            sensor_reset_fsm(sensor);
            break;
    }
}
