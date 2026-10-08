#ifndef SENSOR_APP_H
#define SENSOR_APP_H

#include "max31865.h"

/**
 * @file sensor_app.h
 * @brief Оголошення високорівневого модуля вимірювального тракту та відправки даних через UART.
 */

/**
 * @brief Контекст вимірювального застосунку.
 */
typedef struct {
    max31865_t          driver;             /* Екземпляр низькорівневого C-драйвера MAX31865 */
    UART_HandleTypeDef *huart;              /* Хендл послідовного інтерфейсу STM32 HAL UART */
    volatile bool       drdy_flag;          /* Прапорець готовності нових даних (сигнал DRDY) */
    float               last_temperature;   /* Останнє обчислене значення температури (°C) */
    float               last_resistance;    /* Останній розрахований опір RTD (Ом) */
    uint32_t            measurement_count;  /* Лічильник успішно виконаних вимірювань */
    uint32_t            error_count;        /* Лічильник зафіксованих апаратних помилок */
} max31865_app_t;

/* --- Прототипи функцій вимірювального модуля --- */

/**
 * @brief Ініціалізація високорівневого вимірювального тракту та відправка вітального повідомлення в UART.
 */
max31865_status_t sensor_app_init(max31865_app_t *app, SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin, UART_HandleTypeDef *huart);

/**
 * @brief Обробник переривання EXTI для лінії DRDY (готовність даних від MAX31865).
 */
void sensor_app_on_drdy_interrupt(max31865_app_t *app, uint16_t gpio_pin, uint16_t drdy_pin);

/**
 * @brief Головна функція обробки подій: зчитування АЦП при встановленому прапорці DRDY та відправка телеметрії.
 */
void sensor_app_process(max31865_app_t *app);

/**
 * @brief Форматування та відправка результатів вимірювання у послідовний порт UART.
 */
void sensor_app_transmit_telemetry(max31865_app_t *app, float temp_c, float r_ohms);

/**
 * @brief Форматування та відправка розшифрованого статусу апаратної помилки через UART.
 */
void sensor_app_transmit_error(max31865_app_t *app, uint8_t fault_code);

#endif /* SENSOR_APP_H */
