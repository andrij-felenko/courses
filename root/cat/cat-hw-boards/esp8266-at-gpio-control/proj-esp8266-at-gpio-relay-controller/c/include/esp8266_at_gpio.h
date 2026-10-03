#ifndef ESP8266_AT_GPIO_H
#define ESP8266_AT_GPIO_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "uart_driver.h"

/**
 * @file esp8266_at_gpio.h
 * @brief Оголошення C-драйвера хост-мікроконтролера для керування GPIO ESP8266 через AT-команди.
 * 
 * Включає конфігурацію напрямку виводів (AT+PINMODE), встановлення та зчитування 
 * дискретних логічних рівнів (AT+PINWRITE, AT+PINREAD), а також алгоритми безпечного
 * керування силовим реле з урахуванням конфігураційних виводів завантаження (strapping pins GPIO0, GPIO2, GPIO15).
 */

/**
 * @brief Позначення номери завантажувальних виводів (strapping pins ESP8266).
 */
#define ESP8266_STRAPPING_PIN_GPIO0   0
#define ESP8266_STRAPPING_PIN_GPIO2   2
#define ESP8266_STRAPPING_PIN_GPIO15  15

/**
 * @brief Режими роботи цифрових виводів GPIO.
 */
typedef enum {
    ESP8266_GPIO_MODE_INPUT         = 0,  /**< Вхід без внутрішнього підтягування (Floating) */
    ESP8266_GPIO_MODE_OUTPUT        = 1,  /**< Цифровий вихід (Push-Pull Output) */
    ESP8266_GPIO_MODE_INPUT_PULLUP  = 2,  /**< Вхід з внутрішньою підтяжкою до VCC */
    ESP8266_GPIO_MODE_OUTPUT_OD     = 3   /**< Вихід з відкритим стоком (Open-Drain Output) */
} esp8266_gpio_mode_t;

/**
 * @brief Дискретні логічні рівні на виводах.
 */
typedef enum {
    ESP8266_GPIO_LEVEL_LOW  = 0,  /**< Логічна одиниця / Низький рівень (0 В) */
    ESP8266_GPIO_LEVEL_HIGH = 1   /**< Логічний нуль / Високий рівень (3.3 В) */
} esp8266_gpio_level_t;

/**
 * @brief Коди помилок та результати виконання функцій C-драйвера.
 */
typedef enum {
    ESP8266_GPIO_OK                 =  0,  /**< Операцію виконано успішно */
    ESP8266_GPIO_ERR_INVALID_PARAM  = -1,  /**< Передано некоректний аргумент (недопустимий номер GPIO тощо) */
    ESP8266_GPIO_ERR_TIMEOUT        = -2,  /**< Перевищено тайм-аут очікування відповіді OK/ERROR від UART */
    ESP8266_GPIO_ERR_AT_ERROR       = -3,  /**< Модуль повернув статусну відповідь ERROR */
    ESP8266_GPIO_ERR_UART           = -4,  /**< Сбой передачі/прийому на рівні послідовного порту UART */
    ESP8266_GPIO_ERR_UNRESPONSIVE   = -5   /**< Модуль ESP8266 не відповідає на тестову AT-команду */
} esp8266_gpio_err_t;

/**
 * @brief Конфігураційна структура ініціалізації C-драйвера ESP8266 GPIO.
 */
typedef struct {
    uint32_t default_timeout_ms;          /**< Базовий тайм-аут очікування підтвердження OK/ERROR (мс) */
    uint32_t boot_stabilization_delay_ms; /**< Затримка стабілізації живлення та strapping pins при старті (мс) */
    bool disable_echo;                    /**< Прапорець вимкнення луни команд (ATE0) */
    uart_ring_buffer_t *rx_buffer;        /**< Вказівник на кільцевий буфер UART RX */
    uint32_t (*get_ticks_ms)(void);       /**< Указівник на функцію отримання системного часу в мс */
    void (*delay_ms)(uint32_t ms);        /**< Указівник на функцію системної затримки в мс */
} esp8266_gpio_config_t;

/**
 * @brief Контекст безпечного керування силовим реле.
 * 
 * Зберігає поточний підтверджений стан та активний логічний рівень 
 * спрацьовування реле (Active LOW або Active HIGH).
 */
typedef struct {
    uint8_t gpio_pin;                  /**< Номер виводу GPIO ESP8266, підключеного до реле */
    esp8266_gpio_level_t active_level; /**< Активний логічний рівень увімкнення силової обмотки/оптопари */
    esp8266_gpio_level_t current_level;/**< Поточний підтверджений логічний рівень на виводі */
    bool is_initialized;               /**< Прапорець успішного виконання безпечної ініціалізації */
} esp8266_relay_handle_t;

/* --- Прототипи базових функцій C-драйвера GPIO --- */

/**
 * @brief Ініціалізація C-драйвера ESP8266, перевірка зв'язку та стабілізація при старті.
 * @param config Вказівник на структуру налаштувань.
 * @return ESP8266_GPIO_OK у разі успіху або код помилки.
 */
esp8266_gpio_err_t esp8266_gpio_init(const esp8266_gpio_config_t *config);

/**
 * @brief Конфігурування режиму роботи цифрового виводу ESP8266 (AT+PINMODE).
 * @param pin Номер GPIO виводу (0..16).
 * @param mode Режим роботи (Input, Output, Pullup, Open-Drain).
 * @return ESP8266_GPIO_OK у разі підтвердження OK від ESP8266.
 */
esp8266_gpio_err_t esp8266_gpio_set_mode(uint8_t pin, esp8266_gpio_mode_t mode);

/**
 * @brief Встановлення дискретного логічного рівня на виводі (AT+PINWRITE).
 * @param pin Номер GPIO виводу.
 * @param level Логічний рівень (ESP8266_GPIO_LEVEL_LOW або ESP8266_GPIO_LEVEL_HIGH).
 * @return ESP8266_GPIO_OK при отриманні OK від модуля.
 */
esp8266_gpio_err_t esp8266_gpio_write(uint8_t pin, esp8266_gpio_level_t level);

/**
 * @brief Зчитування поточного логічного рівня на виводі (AT+PINREAD).
 * @param pin Номер GPIO виводу.
 * @param out_level Вказівник для збереження прочитаного значення рівня.
 * @return ESP8266_GPIO_OK при успішному зчитуванні та розборі відповіді +PINREAD.
 */
esp8266_gpio_err_t esp8266_gpio_read(uint8_t pin, esp8266_gpio_level_t *out_level);

/**
 * @brief Перевірка, чи належить вивід до завантажувальних виводів (strapping pins: GPIO0, GPIO2, GPIO15).
 * @param pin Номер GPIO виводу.
 * @return true якщо це strapping pin, false у протилежному випадку.
 */
bool esp8266_gpio_is_strapping_pin(uint8_t pin);

/* --- Прототипи функцій безпечного керування реле --- */

/**
 * @brief Безопасна ініціалізація виводу реле для запобігання хибним спрацьовуванням при старті.
 * @param relay Вказівник на дескриптор реле.
 * @param pin Номер GPIO виводу ESP8266.
 * @param active_level Логічний рівень, який вмикає реле (Active LOW або Active HIGH).
 * @return ESP8266_GPIO_OK у разі успішної конфігурації.
 */
esp8266_gpio_err_t esp8266_relay_init_safe(esp8266_relay_handle_t *relay, uint8_t pin, esp8266_gpio_level_t active_level);

/**
 * @brief Зміна стану реле (увімкнено/вимкнено) з перевіркою відповіді від модуля.
 * @param relay Вказівник на дескриптор реле.
 * @param enable true — увімкнути реле, false — вимкнути.
 * @return ESP8266_GPIO_OK при отриманні підтвердження виконання команди.
 */
esp8266_gpio_err_t esp8266_relay_set_state(esp8266_relay_handle_t *relay, bool enable);

/**
 * @brief Перемикання стану реле на протилежний.
 * @param relay Вказівник на дескриптор реле.
 * @return ESP8266_GPIO_OK при успішному перемиканні.
 */
esp8266_gpio_err_t esp8266_relay_toggle(esp8266_relay_handle_t *relay);

/**
 * @brief Отримання текстового опису коду помилки.
 * @param err Код помилки.
 * @return Рядок з коротким описом помилки українською мовою.
 */
const char* esp8266_gpio_err_to_string(esp8266_gpio_err_t err);

#endif /* ESP8266_AT_GPIO_H */
