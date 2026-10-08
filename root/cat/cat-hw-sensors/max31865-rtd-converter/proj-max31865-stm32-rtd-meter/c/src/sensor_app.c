#include "sensor_app.h"
#include <stdio.h>
#include <string.h>

/**
 * @file sensor_app.c
 * @brief Реалізація подійно-орієнтованого вимірювального тракту та діагностики MAX31865 через UART.
 */

#define UART_TX_TIMEOUT_MS 200

max31865_status_t sensor_app_init(max31865_app_t *app, SPI_HandleTypeDef *hspi, GPIO_TypeDef *cs_port, uint16_t cs_pin, UART_HandleTypeDef *huart)
{
    if (app == NULL || huart == NULL) {
        return MAX31865_ERR_PARAM;
    }

    app->huart = huart;
    app->drdy_flag = false;
    app->last_temperature = 0.0f;
    app->last_resistance = 0.0f;
    app->measurement_count = 0;
    app->error_count = 0;

    /* Конфігурація для датчика PT100 з 3-провідним підключенням та Rref = 430 Ом */
    max31865_config_t config = {
        .rtd_type = MAX31865_RTD_PT100,
        .wire_mode = MAX31865_3WIRE,
        .rref_ohms = 430.0f,
        .filter_50hz = true,
        .auto_conversion = true
    };

    max31865_status_t status = max31865_init(&app->driver, hspi, cs_port, cs_pin, &config);
    if (status == MAX31865_OK) {
        char init_msg[128];
        snprintf(init_msg, sizeof(init_msg),
                 "\r\n=== MAX31865 RTD Converter Driver Initialized ===\r\n"
                 "Config: PT100 | 3-Wire Mode | Rref=430.0 Ohm | 50Hz Filter\r\n\r\n");
        HAL_UART_Transmit(app->huart, (uint8_t *)init_msg, (uint16_t)strlen(init_msg), UART_TX_TIMEOUT_MS);
    }

    return status;
}

void sensor_app_on_drdy_interrupt(max31865_app_t *app, uint16_t gpio_pin, uint16_t drdy_pin)
{
    if (app != NULL && gpio_pin == drdy_pin) {
        app->drdy_flag = true;
    }
}

void sensor_app_transmit_telemetry(max31865_app_t *app, float temp_c, float r_ohms)
{
    if (app == NULL || app->huart == NULL) {
        return;
    }

    char buffer[128];
    snprintf(buffer, sizeof(buffer),
             "[DATA #%lu] Temp: %.2f C | Resistance: %.2f Ohm\r\n",
             (unsigned long)app->measurement_count, temp_c, r_ohms);

    HAL_UART_Transmit(app->huart, (uint8_t *)buffer, (uint16_t)strlen(buffer), UART_TX_TIMEOUT_MS);
}

void sensor_app_transmit_error(max31865_app_t *app, uint8_t fault_code)
{
    if (app == NULL || app->huart == NULL) {
        return;
    }

    char err_buf[256];
    int len = snprintf(err_buf, sizeof(err_buf),
                       "[FAULT #%lu] Hardware Error Detected (0x%02X):\r\n",
                       (unsigned long)app->error_count, fault_code);

    if (fault_code & MAX31865_FAULT_HIGH_THRESH) {
        len += snprintf(err_buf + len, sizeof(err_buf) - len, "  - RTD High Threshold Fault\r\n");
    }
    if (fault_code & MAX31865_FAULT_LOW_THRESH) {
        len += snprintf(err_buf + len, sizeof(err_buf) - len, "  - RTD Low Threshold Fault\r\n");
    }
    if (fault_code & MAX31865_FAULT_REFIN_HIGH) {
        len += snprintf(err_buf + len, sizeof(err_buf) - len, "  - REFIN- > 0.85*VBIAS (Reference Open)\r\n");
    }
    if (fault_code & MAX31865_FAULT_REFIN_LOW) {
        len += snprintf(err_buf + len, sizeof(err_buf) - len, "  - REFIN- < 0.85*VBIAS (FORCE- Open)\r\n");
    }
    if (fault_code & MAX31865_FAULT_RTDIN_LOW) {
        len += snprintf(err_buf + len, sizeof(err_buf) - len, "  - RTDIN- < 0.85*VBIAS (FORCE- Open)\r\n");
    }
    if (fault_code & MAX31865_FAULT_OV_UV) {
        len += snprintf(err_buf + len, sizeof(err_buf) - len, "  - Overvoltage/Undervoltage Fault\r\n");
    }

    HAL_UART_Transmit(app->huart, (uint8_t *)err_buf, (uint16_t)strlen(err_buf), UART_TX_TIMEOUT_MS);
}

void sensor_app_process(max31865_app_t *app)
{
    if (app == NULL) {
        return;
    }

    /* Виконуємо зчитування лише при надходженні сигналу DRDY від MAX31865 */
    if (!app->drdy_flag) {
        return;
    }

    app->drdy_flag = false;

    float temp_c = 0.0f;
    float r_ohms = 0.0f;

    max31865_status_t status = max31865_read_temperature(&app->driver, &temp_c, &r_ohms);

    if (status == MAX31865_OK) {
        app->measurement_count++;
        app->last_temperature = temp_c;
        app->last_resistance = r_ohms;
        sensor_app_transmit_telemetry(app, temp_c, r_ohms);
    } else if (status == MAX31865_ERR_FAULT) {
        app->error_count++;
        sensor_app_transmit_error(app, app->driver.last_fault_status);
        /* Скидання прапорів помилок у мікросхемі для відновлення вимірювального циклу */
        max31865_clear_fault(&app->driver);
    }
}
