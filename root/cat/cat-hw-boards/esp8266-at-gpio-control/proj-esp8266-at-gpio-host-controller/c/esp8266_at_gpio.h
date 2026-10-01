#ifndef ESP8266_AT_GPIO_H
#define ESP8266_AT_GPIO_H

#include <stdint.h>
#include <stdbool.h>

#define RX_BUFFER_SIZE 128
#define TX_BUFFER_SIZE 64

// Стан неблокуючого драйвера (FSM)
typedef enum {
    ESP_STATE_IDLE,          // Очікування нових команд
    ESP_STATE_SENDING_CMD,   // Передача команди в UART
    ESP_STATE_WAIT_RESPONSE, // Очікування OK або ERROR
    ESP_STATE_TIMEOUT,       // Таймаут відповіді
    ESP_STATE_ERROR          // Помилка модуля або невідома відповідь
} esp_fsm_state_t;

// Режим роботи виводу GPIO
typedef enum {
    GPIO_MODE_INPUT = 0,
    GPIO_MODE_OUTPUT = 1
} gpio_mode_t;

// Коллбек-функція для відправки байта через апаратний UART
typedef void (*uart_send_byte_fn)(uint8_t byte);

// Коллбек-функція для сповіщення про асинхронну подію URC (+GPIO_INT:pin,val)
typedef void (*urc_gpio_event_cb_t)(uint8_t pin, uint8_t value);

// Структура контексту драйвера ESP8266 AT GPIO
typedef struct {
    esp_fsm_state_t state;
    uart_send_byte_fn uart_send;
    urc_gpio_event_cb_t urc_callback;
    
    char rx_buffer[RX_BUFFER_SIZE];
    uint16_t rx_index;
    
    uint32_t timer_ms;
    uint32_t timeout_ms;
    bool response_received;
    bool last_command_ok;
} esp8266_driver_t;

// Публічне API драйвера
void esp8266_init(esp8266_driver_t *drv, uart_send_byte_fn send_fn, urc_gpio_event_cb_t urc_cb);
void esp8266_process_rx_byte(esp8266_driver_t *drv, char byte);
void esp8266_update_tick(esp8266_driver_t *drv, uint32_t delta_ms);

bool esp8266_set_gpio_mode(esp8266_driver_t *drv, uint8_t pin, gpio_mode_t mode);
bool esp8266_write_gpio(esp8266_driver_t *drv, uint8_t pin, uint8_t value);
bool esp8266_read_gpio(esp8266_driver_t *drv, uint8_t pin);

#endif // ESP8266_AT_GPIO_H
