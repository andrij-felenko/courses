#include <stdint.h>
#include <stdbool.h>

typedef enum {
    HOST_STATE_IDLE = 0,
    HOST_STATE_CONNECTING,
    HOST_STATE_WAIT_PROMPT,
    HOST_STATE_SENDING_DATA,
    HOST_STATE_WAIT_SEND_OK,
    HOST_STATE_CLOSING,
    HOST_STATE_RECOVERY
} host_fsm_state_t;

typedef struct {
    host_fsm_state_t state;
    uint32_t state_timer;
    uint8_t link_id;
    uint16_t payload_len;
    const uint8_t *payload_ptr;
} host_socket_driver_t;

static host_socket_driver_t driver;

// Неблокуюче оновлення стану драйвера сокета (викликається в головному циклі)
void host_socket_driver_update(uint32_t current_ms) {
    switch (driver.state) {
    case HOST_STATE_IDLE:
        // Очікування події або команди на передачу
        break;

    case HOST_STATE_CONNECTING:
        if (uart_check_response("CONNECT")) {
            // Перехід до запиту на відправку даних
            uart_send_string("AT+CIPSEND=0,64\r\n");
            driver.state = HOST_STATE_WAIT_PROMPT;
            driver.state_timer = current_ms;
        } else if (current_ms - driver.state_timer > 3250) {
            // Таймаут з'єднання — перехід до відновлення
            driver.state = HOST_STATE_RECOVERY;
        }
        break;

    case HOST_STATE_WAIT_PROMPT:
        if (uart_check_response(">")) {
            // Модуль готовий прийняти двійкові дані
            uart_write_bytes(driver.payload_ptr, driver.payload_len);
            driver.state = HOST_STATE_WAIT_SEND_OK;
            driver.state_timer = current_ms;
        } else if (current_ms - driver.state_timer > 2000) {
            driver.state = HOST_STATE_RECOVERY;
        }
        break;

    case HOST_STATE_WAIT_SEND_OK:
        if (uart_check_response("SEND OK")) {
            // Дані успішно відправлені, закриваємо сокет
            uart_send_string("AT+CIPCLOSE=0\r\n");
            driver.state = HOST_STATE_CLOSING;
            driver.state_timer = current_ms;
        } else if (current_ms - driver.state_timer > 3000) {
            driver.state = HOST_STATE_RECOVERY;
        }
        break;

    case HOST_STATE_CLOSING:
        if (uart_check_response("OK") || uart_check_response("CLOSED")) {
            driver.state = HOST_STATE_IDLE;
        } else if (current_ms - driver.state_timer > 1000) {
            driver.state = HOST_STATE_IDLE;
        }
        break;

    case HOST_STATE_RECOVERY:
        // Аварійне закриття сокета та скидання стану
        uart_send_string("AT+CIPCLOSE=0\r\n");
        driver.state = HOST_STATE_IDLE;
        break;
    }
}
