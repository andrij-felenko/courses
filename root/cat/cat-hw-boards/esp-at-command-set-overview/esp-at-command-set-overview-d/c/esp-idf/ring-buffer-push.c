// Приклад реалізації FSM-парсера ESP-AT відповідей на C (ESP-IDF / Generic C)
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define RING_BUF_SIZE 256
#define LINE_BUF_SIZE 128

typedef enum {
    AT_STATE_IDLE,
    AT_STATE_WAIT_RESPONSE,
    AT_STATE_PROCESS_LINE,
    AT_STATE_SUCCESS,
    AT_STATE_ERROR,
    AT_STATE_TIMEOUT
} at_parser_state_t;

typedef struct {
    uint8_t buffer[RING_BUF_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
} ring_buffer_t;

static ring_buffer_t rx_ring_buf = { .head = 0, .tail = 0 };

// Додавання байта в кільцевий буфер з ISR
void ring_buffer_push(uint8_t data) {
    uint16_t next_head = (rx_ring_buf.head + 1) & (RING_BUF_SIZE - 1);
    if (next_head != rx_ring_buf.tail) {
        rx_ring_buf.buffer[rx_ring_buf.head] = data;
        rx_ring_buf.head = next_head;
    }
}

// Зчитування байта з кільцевого буфера
bool ring_buffer_pop(uint8_t *data) {
    if (rx_ring_buf.head == rx_ring_buf.tail) {
        return false; // Буфер порожній
    }
    *data = rx_ring_buf.buffer[rx_ring_buf.tail];
    rx_ring_buf.tail = (rx_ring_buf.tail + 1) & (RING_BUF_SIZE - 1);
    return true;
}

// Функція виділення рядка за термінатором \r\n
bool extract_line(char *line_out, uint16_t max_len) {
    static char line_buf[LINE_BUF_SIZE];
    static uint16_t line_pos = 0;
    uint8_t ch;

    while (ring_buffer_pop(&ch)) {
        if (ch == '\r') {
            continue; // Пропускаємо \r
        } else if (ch == '\n') {
            if (line_pos > 0) {
                line_buf[line_pos] = '\0';
                strncpy(line_out, line_buf, max_len);
                line_pos = 0;
                return true; // Рядок виділено
            }
        } else if (line_pos < LINE_BUF_SIZE - 1) {
            line_buf[line_pos++] = (char)ch;
        }
    }
    return false;
}

// Основний процес обробки FSM
at_parser_state_t process_at_parser(uint32_t current_time_ms, uint32_t timeout_ms) {
    static at_parser_state_t state = AT_STATE_IDLE;
    static uint32_t start_time = 0;
    char current_line[LINE_BUF_SIZE];

    if (state == AT_STATE_WAIT_RESPONSE) {
        if (extract_line(current_line, sizeof(current_line))) {
            // Класифікація виділеного рядка
            if (strcmp(current_line, "OK") == 0) {
                state = AT_STATE_SUCCESS;
            } else if (strcmp(current_line, "ERROR") == 0 || strncmp(current_line, "+CME ERROR", 10) == 0) {
                state = AT_STATE_ERROR;
            } else if (strncmp(current_line, "+", 1) == 0 || strncmp(current_line, "WIFI", 4) == 0) {
                // Окремий обробник асинхронних сповіщень URC
                printf("URC Event: %s\n", current_line);
            }
        } else if ((current_time_ms - start_time) >= timeout_ms) {
            state = AT_STATE_TIMEOUT;
        }
    }
    return state;
}
