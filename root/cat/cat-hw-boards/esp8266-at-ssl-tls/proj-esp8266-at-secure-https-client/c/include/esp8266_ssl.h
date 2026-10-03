#ifndef ESP8266_SSL_H
#define ESP8266_SSL_H

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "ring_buffer.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Режими верифікації сертифікатів SSL/TLS для команди AT+CIPSSLCCONF.
 */
typedef enum {
    ESP8266_TLS_AUTH_NONE = 0,            /**< Верифікація вимкнена (No verification) */
    ESP8266_TLS_AUTH_VERIFY_SERVER = 1,   /**< Перевірка сертифіката сервера за допомогою CA */
    ESP8266_TLS_AUTH_CLIENT_CERT = 2,     /**< Аутентифікація за допомогою клієнтського сертифіката */
    ESP8266_TLS_AUTH_MUTUAL = 3           /**< Двостороння TLS-аутентифікація (Mutual Authentication) */
} esp8266_tls_auth_mode_t;

/**
 * @brief Перелічення станів неблокуючого скінченного автомата (FSM) драйвера ESP8266 SSL.
 */
typedef enum {
    ESP8266_SSL_STATE_IDLE = 0,           /**< Очікування нових команд */
    ESP8266_SSL_STATE_CONFIGURING_TLS,    /**< Налаштування параметрів SSL/TLS (AT+CIPSSLCCONF/CSNI/CSZ) */
    ESP8266_SSL_STATE_CONNECTING,         /**< Встановлення SSL-з'єднання (AT+CIPSTART) */
    ESP8266_SSL_STATE_SENDING_CMD,        /**< Відправка AT-команд підготовки */
    ESP8266_SSL_STATE_WAIT_PROMPT,        /**< Очікування символу-запрошення '>' від AT+CIPSEND */
    ESP8266_SSL_STATE_SENDING_PAYLOAD,     /**< Передача заголовків та тіла HTTP-запиту */
    ESP8266_SSL_STATE_WAIT_RESPONSE,      /**< Очікування відповіді сервера або кадрів +IPD */
    ESP8266_SSL_STATE_READING_IPD,        /**< Розбір та зчитування корисного навантаження +IPD */
    ESP8266_SSL_STATE_CLOSING,            /**< Завершення SSL-сесії (AT+CIPCLOSE) */
    ESP8266_SSL_STATE_ERROR               /**< Стан помилки рукостискання, таймауту або зв'язку */
} esp8266_ssl_state_t;

/**
 * @brief Статуси виконання методів C-драйвера.
 */
typedef enum {
    ESP8266_SSL_OK = 0,                   /**< Успішне виконання операції */
    ESP8266_SSL_ERROR = -1,               /**< Загальна помилка AT-інтерпретатора */
    ESP8266_SSL_TIMEOUT = -2,             /**< Превищення ліміту часу очікування відповіді */
    ESP8266_SSL_BUSY = -3,                /**< Драйвер зайнятий виконанням іншої операції */
    ESP8266_SSL_ERR_HANDSHAKE = -4,       /**< Помилка TLS-рукостискання чи відхилення сертифіката */
    ESP8266_SSL_ERR_CERT = -5,            /**< Невдала валідація CA-сертифіката */
    ESP8266_SSL_ERR_CLOSED = -6           /**< З'єднання передчасно розірвано сервером */
} esp8266_ssl_status_t;

/**
 * @brief Параметри конфігурації TLS-сесії хоста.
 */
typedef struct {
    esp8266_tls_auth_mode_t auth_mode;   /**< Режим верифікації сертифіката */
    char sni_hostname[128];               /**< Заголовок SNI (Server Name Indication) */
    uint16_t buffer_size;                 /**< Розмір SSL буфера у DRAM модулі (наприклад 4096) */
    uint32_t handshake_timeout_ms;        /**< Ліміт часу виконання SSL-рукостискання */
} esp8266_tls_config_t;

/**
 * @brief Буфер збереження та розбору HTTP/HTTPS відповіді.
 */
typedef struct {
    int status_code;             /**< Числовий код статусу HTTP (наприклад 200, 404, 500) */
    char status_text[32];        /**< Рядкове пояснення статусу (наприклад "OK", "Not Found") */
    bool headers_parsed;         /**< Ознака завершення парсингу заголовків HTTP */
    bool is_complete;            /**< Ознака повного завершення зчитування пакета */
    uint8_t *body_buf;           /**< Вказівник на буфер для збереження тіла відповіді */
    size_t body_len;             /**< Поточна кількість зчитаних байтів тіла */
    size_t body_capacity;        /**< Максимальна ємність наданого буфера */
} http_response_t;

/**
 * @brief Абстракції периферійних функцій хост-мікроконтролера.
 */
typedef void (*esp8266_uart_tx_fn)(const uint8_t *data, size_t len);
typedef uint32_t (*esp8266_get_ticks_ms_fn)(void);
typedef void (*esp8266_delay_ms_fn)(uint32_t ms);

/**
 * @brief Контекстний об'єкт C-драйвера ESP8266 SSL.
 */
typedef struct {
    ring_buffer_t *rx_rb;                 /**< Кільцевий буфер прийому UART RX */
    esp8266_uart_tx_fn tx_fn;             /**< Функція передачі байтів в UART */
    esp8266_get_ticks_ms_fn ticks_fn;     /**< Зворотний виклик системного таймера (мілісекунди) */
    esp8266_delay_ms_fn delay_fn;         /**< Зворотний виклик для неблокуючих паузок */
    esp8266_ssl_state_t state;            /**< Поточний стан FSM-автомата */
    esp8266_tls_config_t tls_config;      /**< Активна конфігурація TLS */
    bool is_connected;                    /**< Статус відкритого SSL-сокету */
    uint32_t state_timer;                 /**< Часова мітка початку поточного стану */
} esp8266_ssl_ctx_t;

/**
 * @brief Ініціалізація структури HTTP відповіді.
 * @param resp Вказівник на об'єкт відповіді.
 * @param body_buf Зовнішній буфер для накопичення тіла відповіді.
 * @param body_cap Максимальний розмір буфера.
 */
void http_response_init(http_response_t *resp, uint8_t *body_buf, size_t body_cap);

/**
 * @brief Скидання вмісту та прапорців HTTP відповіді перед новим запитом.
 * @param resp Вказівник на об'єкт відповіді.
 */
void http_response_clear(http_response_t *resp);

/**
 * @brief Ініціалізація C-драйвера ESP8266 SSL.
 * @param ctx Вказівник на контекст драйвера.
 * @param rx_rb Вказівник на кільцевий буфер UART.
 * @param tx_fn Зворотний виклик передачі UART.
 * @param ticks_fn Зворотний виклик таймера системного часу.
 * @param delay_fn Зворотний виклик системної затримки.
 * @return ESP8266_SSL_OK при успіху, інакше код помилки.
 */
esp8266_ssl_status_t esp8266_ssl_init(esp8266_ssl_ctx_t *ctx,
                                       ring_buffer_t *rx_rb,
                                       esp8266_uart_tx_fn tx_fn,
                                       esp8266_get_ticks_ms_fn ticks_fn,
                                       esp8266_delay_ms_fn delay_fn);

/**
 * @brief Налаштування параметрів SSL/TLS (AT+CIPSSLCCONF, AT+CIPSSLCSNI, AT+CIPSSLCSZ).
 * @param ctx Вказівник на контекст драйвера.
 * @param config Вказівник на структуру конфігурації TLS.
 * @return ESP8266_SSL_OK при успіху, інакше код помилки.
 */
esp8266_ssl_status_t esp8266_ssl_configure_tls(esp8266_ssl_ctx_t *ctx,
                                                const esp8266_tls_config_t *config);

/**
 * @brief Встановлення захищеного SSL/TLS з'єднання (AT+CIPSTART="SSL",...).
 * @param ctx Вказівник на контекст драйвера.
 * @param host Доменне ім'я або IP-адреса сервера.
 * @param port Порт сервера (зазвичай 443 для HTTPS).
 * @param timeout_ms Максимальний час очікування встановлення рукостискання.
 * @return ESP8266_SSL_OK при успіху, інакше код помилки.
 */
esp8266_ssl_status_t esp8266_ssl_connect(esp8266_ssl_ctx_t *ctx,
                                         const char *host,
                                         uint16_t port,
                                         uint32_t timeout_ms);

/**
 * @brief Безпечне закриття сесії SSL (AT+CIPCLOSE).
 * @param ctx Вказівник на контекст драйвера.
 * @return ESP8266_SSL_OK при успіху.
 */
esp8266_ssl_status_t esp8266_ssl_close(esp8266_ssl_ctx_t *ctx);

/**
 * @brief Виконання HTTPS GET запиту.
 * @param ctx Вказівник на контекст драйвера.
 * @param host Ім'я хоста сервера.
 * @param port Порт з'єднання (443).
 * @param path Шлях ресурсу (наприклад "/api/v1/data").
 * @param response Буфер для збереження результатів відповіді.
 * @param timeout_ms Загальний таймаут виконання запиту.
 * @return ESP8266_SSL_OK при успіху, інакше код помилки.
 */
esp8266_ssl_status_t esp8266_ssl_http_get(esp8266_ssl_ctx_t *ctx,
                                           const char *host,
                                           uint16_t port,
                                           const char *path,
                                           http_response_t *response,
                                           uint32_t timeout_ms);

/**
 * @brief Виконання HTTPS POST запиту з передачею корисного навантаження.
 * @param ctx Вказівник на контекст драйвера.
 * @param host Ім'я хоста сервера.
 * @param port Порт з'єднання (443).
 * @param path Шлях ресурсу.
 * @param content_type MIME-тип даних (наприклад "application/json").
 * @param body Вказівник на байти корисного навантаження тіла.
 * @param body_len Довжина тіла запиту у байтах.
 * @param response Буфер для збереження результатів відповіді.
 * @param timeout_ms Загальний таймаут виконання запиту.
 * @return ESP8266_SSL_OK при успіху, інакше код помилки.
 */
esp8266_ssl_status_t esp8266_ssl_http_post(esp8266_ssl_ctx_t *ctx,
                                            const char *host,
                                            uint16_t port,
                                            const char *path,
                                            const char *content_type,
                                            const uint8_t *body,
                                            size_t body_len,
                                            http_response_t *response,
                                            uint32_t timeout_ms);

/**
 * @brief Фонова функція оновлення FSM-автомата (викликається в головному циклі).
 * @param ctx Вказівник на контекст драйвера.
 */
void esp8266_ssl_process(esp8266_ssl_ctx_t *ctx);

/**
 * @brief Отримання поточного стану FSM.
 * @param ctx Вказівник на контекст.
 * @return Поточний стан esp8266_ssl_state_t.
 */
esp8266_ssl_state_t esp8266_ssl_get_state(const esp8266_ssl_ctx_t *ctx);

#ifdef __cplusplus
}
#endif

#endif /* ESP8266_SSL_H */
