#include <stdio.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include "esp_timer.h"

#define RING_BUF_SIZE 576
#define LINE_BUF_SIZE 256
#define CMD_TIMEOUT_MS 2000

// Стани FSM розбірника
typedef enum {
    FSM_STATE_IDLE,
    FSM_STATE_ACCUMULATING,
    FSM_STATE_EVALUATE,
    FSM_STATE_TIMEOUT,
    FSM_STATE_ERROR
} fsm_state_t;

// Результат виконання FSM
typedef enum {
    FSM_RES_BUSY_PROCESSING,
    FSM_RES_OK,
    FSM_RES_ERROR,
    FSM_RES_FAIL,
    FSM_RES_TIMEOUT,
    FSM_RES_URC_DETECTED
} fsm_result_t;

// Кільцевий буфер для ізоляції UART переривань
typedef struct {
    uint8_t data[RING_BUF_SIZE];
    uint16_t head;
    uint16_t tail;
} ring_buffer_t;

static void ring_buf_init(ring_buffer_t *rb) {
    rb->head = 0;
    rb->tail = 0;
}

static bool ring_buf_push(ring_buffer_t *rb, uint8_t byte) {
    uint16_t next = (rb->head + 1) % RING_BUF_SIZE;
    if (next == rb->tail) {
        return false; // Буфер переповнено
    }
    rb->data[rb->head] = byte;
    rb->head = next;
    return true;
}

static bool ring_buf_pop(ring_buffer_t *rb, uint8_t *byte) {
    if (rb->head == rb->tail) {
        return false; // Буфер порожній
    }
    *byte = rb->data[rb->tail];
    rb->tail = (rb->tail + 1) % RING_BUF_SIZE;
    return true;
}

static void ring_buf_flush(ring_buffer_t *rb) {
    rb->head = 0;
    rb->tail = 0;
}

// Контекст FSM-драйвера
typedef struct {
    fsm_state_t state;
    char line_buf[LINE_BUF_SIZE];
    uint16_t line_idx;
    int64_t start_time_ms;
    ring_buffer_t rx_rb;
} at_fsm_parser_t;

void at_parser_init(at_fsm_parser_t *parser) {
    parser->state = FSM_STATE_IDLE;
    parser->line_idx = 0;
    parser->start_time_ms = 0;
    ring_buf_init(&parser->rx_rb);
}

// Ресинхронізація каналу після помилок чи таймаутів
void at_parser_resync(at_fsm_parser_t *parser) {
    ring_buf_flush(&parser->rx_rb);
    parser->line_idx = 0;
    parser->state = FSM_STATE_IDLE;
}

// Обробка вхідного потоку у FSM
fsm_result_t at_parser_process(at_fsm_parser_t *parser) {
    int64_t now_ms = esp_timer_get_time() / 1000;
    
    // Перевірка загального таймауту виконання
    if (parser->state != FSM_STATE_IDLE && (now_ms - parser->start_time_ms) > CMD_TIMEOUT_MS) {
        parser->state = FSM_STATE_TIMEOUT;
        at_parser_resync(parser);
        return FSM_RES_TIMEOUT;
    }

    uint8_t ch;
    while (ring_buf_pop(&parser->rx_rb, &ch)) {
        if (parser->state == FSM_STATE_IDLE) {
            parser->state = FSM_STATE_ACCUMULATING;
            parser->start_time_ms = now_ms;
        }

        if (ch == '\n') {
            // Завершення рядка, видалення \r за наявності
            if (parser->line_idx > 0 && parser->line_buf[parser->line_idx - 1] == '\r') {
                parser->line_buf[parser->line_idx - 1] = '\0';
            } else {
                parser->line_buf[parser->line_idx] = '\0';
            }

            parser->state = FSM_STATE_EVALUATE;

            // Перевірка термінальних статусів
            if (strcmp(parser->line_buf, "OK") == 0) {
                parser->state = FSM_STATE_IDLE;
                parser->line_idx = 0;
                return FSM_RES_OK;
            }
            if (strcmp(parser->line_buf, "ERROR") == 0) {
                parser->state = FSM_STATE_IDLE;
                parser->line_idx = 0;
                return FSM_RES_ERROR;
            }
            if (strcmp(parser->line_buf, "FAIL") == 0) {
                parser->state = FSM_STATE_IDLE;
                parser->line_idx = 0;
                return FSM_RES_FAIL;
            }

            // Перевірка на асинхронні URC
            if (strncmp(parser->line_buf, "WIFI ", 5) == 0 || strncmp(parser->line_buf, "ready", 5) == 0) {
                parser->line_idx = 0;
                parser->state = FSM_STATE_ACCUMULATING;
                return FSM_RES_URC_DETECTED;
            }

            // Рядок корисних даних (Payload) — скидання індексу для наступного рядка
            parser->line_idx = 0;
            parser->state = FSM_STATE_ACCUMULATING;
        } else if (ch != '\r') {
            if (parser->line_idx < (LINE_BUF_SIZE - 1)) {
                parser->line_buf[parser->line_idx++] = (char)ch;
            } else {
                // Переповнення буфера рядка — ресинхронізація
                at_parser_resync(parser);
                return FSM_RES_ERROR;
            }
        }
    }

    return FSM_RES_BUSY_PROCESSING;
}
