#ifndef ESP_CIPSEND_FSM_H
#define ESP_CIPSEND_FSM_H

#include <stdint.h>
#include <stdbool.h>

// Стани скінченного автомата
typedef enum {
    CIPSEND_STATE_IDLE,
    CIPSEND_STATE_WAIT_PROMPT,
    CIPSEND_STATE_WAIT_OK,
    CIPSEND_STATE_ERROR
} esp_cipsend_state_t;

// Структура для прив'язки апаратно-залежних функцій UART
typedef struct {
    void (*uart_write)(const uint8_t *data, uint16_t len);
    bool (*uart_read_char)(uint8_t *c);
    uint32_t (*get_tick_ms)(void);
} esp_uart_hal_t;

// Контекст (екземпляр) драйвера
typedef struct {
    esp_cipsend_state_t state;
    esp_uart_hal_t *hal;
    const uint8_t *tx_data;
    uint16_t tx_len;
    uint32_t timer_start;
    uint32_t timeout_ms;
} esp_cipsend_t;

// Ініціалізація автомата
void esp_cipsend_init(esp_cipsend_t *ctx, esp_uart_hal_t *hal);

// Запуск процесу передачі (неблокуючий)
bool esp_cipsend_start(esp_cipsend_t *ctx, const uint8_t *data, uint16_t len, uint32_t timeout_ms);

// Головна tick-функція FSM, яка має викликатись регулярно в циклі
void esp_cipsend_tick(esp_cipsend_t *ctx);

// Отримання поточного стану (для перевірки завершення)
esp_cipsend_state_t esp_cipsend_get_state(const esp_cipsend_t *ctx);

#endif // ESP_CIPSEND_FSM_H
