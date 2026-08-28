/* c */
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define LOOP_BUF_SIZE 256
#define MAX_FRAME_LEN 64

// Коди станів та помилок струмової петлі
typedef enum {
    CURRENT_LOOP_OK = 0,
    CURRENT_LOOP_ERR_EMPTY,
    CURRENT_LOOP_ERR_FULL,
    CURRENT_LOOP_ERR_LINE_BREAK,  // Аварія: обрив петлі (0 мА тривалий Space)
    CURRENT_LOOP_ERR_CHECKSUM,    // Похибка контрольної суми
    CURRENT_LOOP_ERR_OVERFLOW
} loop_status_t;

// Структура кільцевого буфера з фіксацією помилок лінії
typedef struct {
    uint8_t buffer[LOOP_BUF_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
    volatile bool line_break_fault; // Прапор аварійного обриву струму
    uint32_t break_events_count;
} current_loop_ringbuf_t;

// Структура прийнятого пакета
typedef struct {
    uint8_t data[MAX_FRAME_LEN];
    uint8_t length;
    uint8_t sender_id;
} loop_frame_t;

// Ініціалізація буфера
void loop_buf_init(current_loop_ringbuf_t *rb) {
    rb->head = 0;
    rb->tail = 0;
    rb->line_break_fault = false;
    rb->break_events_count = 0;
}

// Запис байта з обробника переривання UART (ISR)
// Якщо rx_break == true, апаратний UART зафіксував Break Condition (обрив петлі)
void loop_buf_isr_push(current_loop_ringbuf_t *rb, uint8_t byte, bool rx_break) {
    if (rx_break) {
        rb->line_break_fault = true;
        rb->break_events_count++;
        return;
    }

    uint16_t next_head = (rb->head + 1) % LOOP_BUF_SIZE;
    if (next_head != rb->tail) {
        rb->buffer[rb->head] = byte;
        rb->head = next_head;
    }
}

// Зчитування байта з буфера у головному циклі
loop_status_t loop_buf_pop(current_loop_ringbuf_t *rb, uint8_t *byte) {
    if (rb->line_break_fault) {
        return CURRENT_LOOP_ERR_LINE_BREAK;
    }

    if (rb->head == rb->tail) {
        return CURRENT_LOOP_ERR_EMPTY;
    }

    *byte = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) % LOOP_BUF_SIZE;
    return CURRENT_LOOP_OK;
}

// Скинути прапор аварії після відновлення струму в петлі
void loop_buf_clear_fault(current_loop_ringbuf_t *rb) {
    rb->line_break_fault = false;
}

// Парсер кадрів пакета струмової петлі
// Формат пакета: [SOF = 0x02] [LEN] [SENDER_ID] [PAYLOAD...] [CRC8]
loop_status_t loop_parse_frame(current_loop_ringbuf_t *rb, loop_frame_t *frame) {
    uint8_t byte;
    loop_status_t status = loop_buf_pop(rb, &byte);
    
    if (status != CURRENT_LOOP_OK) {
        return status;
    }

    // Пошук маркера початку кадру (SOF)
    if (byte != 0x02) {
        return CURRENT_LOOP_ERR_EMPTY;
    }

    // Зчитуємо довжину
    uint8_t len = 0;
    while ((status = loop_buf_pop(rb, &len)) == CURRENT_LOOP_ERR_EMPTY);
    if (status != CURRENT_LOOP_OK) return status;
    
    if (len > MAX_FRAME_LEN) return CURRENT_LOOP_ERR_OVERFLOW;

    // Зчитуємо ID відправника
    while ((status = loop_buf_pop(rb, &frame->sender_id)) == CURRENT_LOOP_ERR_EMPTY);
    if (status != CURRENT_LOOP_OK) return status;

    // Зчитуємо корисне навантаження
    uint8_t crc = 0x00 ^ len ^ frame->sender_id;
    for (uint8_t i = 0; i < len; i++) {
        while ((status = loop_buf_pop(rb, &frame->data[i])) == CURRENT_LOOP_ERR_EMPTY);
        if (status != CURRENT_LOOP_OK) return status;
        crc ^= frame->data[i];
    }

    // Зчитуємо контрольне значення CRC
    uint8_t rx_crc = 0;
    while ((status = loop_buf_pop(rb, &rx_crc)) == CURRENT_LOOP_ERR_EMPTY);
    if (status != CURRENT_LOOP_OK) return status;

    if (crc != rx_crc) {
        return CURRENT_LOOP_ERR_CHECKSUM;
    }

    frame->length = len;
    return CURRENT_LOOP_OK;
}
