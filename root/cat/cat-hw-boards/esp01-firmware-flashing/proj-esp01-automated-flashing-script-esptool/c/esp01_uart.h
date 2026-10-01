#ifndef ESP01_UART_H
#define ESP01_UART_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Коди помилок роботи драйвера ESP-01 */
typedef enum {
    ESP01_OK = 0,
    ESP01_ERR_PORT_OPEN = -1,
    ESP01_ERR_PORT_CONFIG = -2,
    ESP01_ERR_TIMEOUT = -3,
    ESP01_ERR_NO_RESPONSE = -4,
    ESP01_ERR_BUFFER_OVERFLOW = -5
} esp01_err_t;

/* Структура конфігурації з'єднання UART */
typedef struct {
    const char *port_name;    /* Шлях до пристрою порту (наприклад, "/dev/ttyUSB0") */
    uint32_t baud_rate;       /* Швидкість обміну (наприклад, 115200 бод) */
    uint32_t timeout_ms;      /* Таймаут очікування відповіді у мілісекундах */
} esp01_config_t;

/* Структура результатів діагностики та стану модуля ESP-01 */
typedef struct {
    bool is_connected;        /* Прапор наявності зв'язку з модулем (відповідь "OK") */
    bool is_ready;            /* Прапор готовності системи до роботи ("ready") */
    char firmware_rev[64];    /* Буфер для збереження версії прошивки (команда AT+GMR) */
} esp01_status_t;

/* Структура дескриптора драйвера ESP-01 */
typedef struct {
    int port_fd;              /* Файловий дескриптор відкритого послідовного порту */
    esp01_config_t config;    /* Поточні налаштування з'єднання */
    bool is_initialized;      /* Прапор ініціалізації драйвера */
} esp01_driver_t;

/* Публічний програмний інтерфейс (API) драйвера ESP-01 */
esp01_err_t esp01_init(esp01_driver_t *driver, const esp01_config_t *config);
esp01_err_t esp01_close(esp01_driver_t *driver);
esp01_err_t esp01_ping(esp01_driver_t *driver);
esp01_err_t esp01_get_status(esp01_driver_t *driver, esp01_status_t *status);

#endif /* ESP01_UART_H */
