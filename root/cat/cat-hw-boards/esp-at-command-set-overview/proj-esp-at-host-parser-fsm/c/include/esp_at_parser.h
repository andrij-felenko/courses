#ifndef ESP_AT_PARSER_H
#define ESP_AT_PARSER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include "ring_buffer.h"

/**
 * @file esp_at_parser.h
 * @brief Оголошення розширеного FSM-парсера AT-відповідей ESP8266.
 *
 * Забезпечує неблокуючий розбір вхідних даних з кільцевого буфера, 
 * конфігурацію колбеків статусів (OK, ERROR, BUSY, TIMEOUT) та автоматичне 
 * відновлення за системним таймером.
 */

#ifdef __cplusplus
extern "C" {
#endif

/** @brief Максимальний розмір буфера рядка для збереження кадру відповіді */
#define ESP_AT_LINE_BUF_SIZE 128

/**
 * @brief Перелік станів скінченного автомата (FSM) розбору AT-команд.
 */
typedef enum {
    ESP_AT_STATE_IDLE = 0,         /**< Очікування початку нової відповіді */
    ESP_AT_STATE_SEARCH_CR,        /**< Накопичення символів рядка до появи \r */
    ESP_AT_STATE_SEARCH_LF,        /**< Перевірка наступного термінаторного символу \n */
    ESP_AT_STATE_PROCESSING_LINE,  /**< Аналіз виділеного текстового рядка */
    ESP_AT_STATE_TIMEOUT_RECOVERY, /**< Скидання стану автомата після таймауту */
    ESP_AT_STATE_MAX               /**< Кількість станів FSM */
} esp_at_state_t;

/**
 * @brief Перелік статусних відповідей та подій AT-парсера.
 */
typedef enum {
    ESP_AT_STATUS_OK = 0,     /**< Отримано відповідь OK */
    ESP_AT_STATUS_ERROR,      /**< Отримано відповідь ERROR або FAIL */
    ESP_AT_STATUS_BUSY,       /**< Отримано відповідь BUSY (busy p... / busy s...) */
    ESP_AT_STATUS_TIMEOUT,    /**< Перевищено тайм-аут очікування відповіді */
    ESP_AT_STATUS_UNSOLICITED /**< Незапитуване повідомлення (URC) */
} esp_at_status_t;

/* Форвардні оголошення структури контексту парсера */
struct esp_at_parser;
typedef struct esp_at_parser esp_at_parser_t;

/**
 * @brief Вказівник на функцію зворотного виклику для статусних подій (OK, ERROR, BUSY, TIMEOUT).
 */
typedef void (*esp_at_status_cb_t)(esp_at_status_t status, void *user_data);

/**
 * @brief Вказівник на функцію зворотного виклику для обробки текстових рядків відповіді.
 */
typedef void (*esp_at_line_cb_t)(const char *line, size_t length, void *user_data);

/**
 * @brief Вказівник на обробник стану у таблиці станів FSM.
 */
typedef void (*esp_at_state_handler_t)(esp_at_parser_t *parser, uint8_t byte);

/**
 * @brief Структура контексту неблокуючого FSM-парсера AT-відповідей.
 */
struct esp_at_parser {
    ring_buffer_t *rx_buf;               /**< Вказівник на вхідний кільцевий буфер UART */
    esp_at_state_t state;                /**< Поточний стан FSM-автомата */
    
    char line_buf[ESP_AT_LINE_BUF_SIZE]; /**< Внутрішній буфер для накопичення поточного рядка */
    uint16_t line_len;                   /**< Поточна довжина накопиченого рядка */
    
    /* Колбеки подій */
    esp_at_status_cb_t on_ok;            /**< Колбек на статус OK */
    esp_at_status_cb_t on_error;         /**< Колбек на статус ERROR */
    esp_at_status_cb_t on_busy;          /**< Колбек на статус BUSY */
    esp_at_status_cb_t on_timeout;       /**< Колбек на статус TIMEOUT */
    esp_at_line_cb_t on_line;            /**< Колбек для отриманих рядків даних */
    
    void *user_data;                     /**< Указівник на дані користувача (контекст додатку) */
    
    /* Таймери та таймаути */
    uint32_t (*get_system_time_ms)(void);/**< Вказівник на системну функцію часу (мс) */
    uint32_t command_start_time_ms;     /**< Час відправки останньої AT-команди */
    uint32_t last_char_time_ms;          /**< Час прийому останнього символу */
    uint32_t timeout_period_ms;          /**< Встановлений інтервал таймауту очікування */
    bool is_waiting_response;            /**< Прапорець очікування відповіді на відправлену команду */
};

/**
 * @brief Ініціалізація контексту FSM-парсера AT-відповідей.
 *
 * @param parser Вказівник на контекст парсера.
 * @param rx_buf Вказівник на ініціалізований кільцевий буфер.
 * @param get_time_ms Вказівник на функцію отримання поточного часу в мс.
 */
void esp_at_parser_init(esp_at_parser_t *parser, ring_buffer_t *rx_buf, uint32_t (*get_time_ms)(void));

/**
 * @brief Налаштування контексту даних користувача для колбеків.
 *
 * @param parser Вказівник на контекст парсера.
 * @param user_data Вказівник на довільні дані користувача.
 */
void esp_at_parser_set_user_data(esp_at_parser_t *parser, void *user_data);

/**
 * @brief Реєстрація системних функцій зворотного виклику для статусних відповідей.
 *
 * @param parser Вказівник на контекст парсера.
 * @param on_ok Обробник статусу OK (може бути NULL).
 * @param on_error Обробник статусу ERROR (може бути NULL).
 * @param on_busy Обробник статусу BUSY (може бути NULL).
 * @param on_timeout Обробник події таймауту (може бути NULL).
 */
void esp_at_parser_register_callbacks(esp_at_parser_t *parser,
                                       esp_at_status_cb_t on_ok,
                                       esp_at_status_cb_t on_error,
                                       esp_at_status_cb_t on_busy,
                                       esp_at_status_cb_t on_timeout);

/**
 * @brief Реєстрація колбеку для передачі виділених текстових рядків.
 *
 * @param parser Вказівник на контекст парсера.
 * @param on_line Функція обробки текстового рядка.
 */
void esp_at_parser_register_line_callback(esp_at_parser_t *parser, esp_at_line_cb_t on_line);

/**
 * @brief Початок очікування відповіді на надсилаєму AT-команду з контролем таймауту.
 *
 * @param parser Вказівник на контекст парсера.
 * @param timeout_ms Інтервал таймауту в мілісекундах.
 */
void esp_at_parser_start_command(esp_at_parser_t *parser, uint32_t timeout_ms);

/**
 * @brief Посимвольна обробка вхідного байта через таблицю станів FSM.
 *
 * @param parser Вказівник на контекст парсера.
 * @param byte Вхідний символ з кільцевого буфера.
 */
void esp_at_parser_process_byte(esp_at_parser_t *parser, uint8_t byte);

/**
 * @brief Вигребти та обробити всі накопичені байти з кільцевого буфера (викликається в main loop).
 *
 * @param parser Вказівник на контекст парсера.
 */
void esp_at_parser_process_buffer(esp_at_parser_t *parser);

/**
 * @brief Перевірка перевищення тайм-ауту очікування відповіді та відновлення стану FSM.
 *
 * @param parser Вказівник на контекст парсера.
 */
void esp_at_parser_check_timeout(esp_at_parser_t *parser);

/**
 * @brief Своєчасне скидання FSM парсера у початковий стан IDLE.
 *
 * @param parser Вказівник на контекст парсера.
 */
void esp_at_parser_reset(esp_at_parser_t *parser);

/**
 * @brief Отримання поточного стану FSM парсера.
 *
 * @param parser Вказівник на контекст парсера.
 * @return Поточний стан esp_at_state_t.
 */
esp_at_state_t esp_at_parser_get_state(const esp_at_parser_t *parser);

/**
 * @brief Перевірка, чи чекає парсер на завершення виконання AT-команди.
 *
 * @param parser Вказівник на контекст парсера.
 * @return true Якщо команда обробляється, false якщо парсер вільний.
 */
bool esp_at_parser_is_busy(const esp_at_parser_t *parser);

#ifdef __cplusplus
}
#endif

#endif /* ESP_AT_PARSER_H */
