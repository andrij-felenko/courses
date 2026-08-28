/**
 * @file event_queue.h
 * @brief Безблокувальна черга часових міток подій на C99
 */

#ifndef EVENT_QUEUE_H
#define EVENT_QUEUE_H

#include <stdint.h>
#include <stdbool.h>

#define EVENT_QUEUE_CAPACITY 64U /* Степінь двійки для швидкого маскування */
#define EVENT_QUEUE_MASK     (EVENT_QUEUE_CAPACITY - 1U)

typedef struct {
    uint32_t timestamp_us; /**< Апаратна мітка таймера DWT/TIM в мікросекундах */
    uint8_t  channel_id;   /**< Номер фізичного входу (0..31) */
    bool     edge_level;   /**< Напрямок перепаду (true = 0->1, false = 1->0) */
} event_record_t;

typedef struct {
    event_record_t buffer[EVENT_QUEUE_CAPACITY];
    volatile uint32_t head; /**< Індекс запису (модифікується лише в ISR) */
    volatile uint32_t tail; /**< Індекс читання (модифікується лише в фоні) */
} event_queue_t;

static inline void event_queue_init(event_queue_t *q) {
    q->head = 0U;
    q->tail = 0U;
}

/**
 * @brief Додавання події з ISR без блокувань за 4 такти
 */
static inline bool event_queue_push_isr(event_queue_t *q, uint8_t ch, bool level, uint32_t ts) {
    uint32_t current_head = q->head;
    uint32_t next_head = (current_head + 1U) & EVENT_QUEUE_MASK;

    if (next_head == q->tail) {
        return false; /* Переповнення черги (Queue Overflow) */
    }

    q->buffer[current_head].channel_id   = ch;
    q->buffer[current_head].edge_level   = level;
    q->buffer[current_head].timestamp_us = ts;

    /* Бар'єр пам'яті для гарантії завершення запису перед публікацією індексу */
    __asm volatile("" ::: "memory");
    q->head = next_head;
    return true;
}

/**
 * @brief Вичитування події у фоновому потоці
 */
static inline bool event_queue_pop_main(event_queue_t *q, event_record_t *out_ev) {
    uint32_t current_tail = q->tail;
    if (current_tail == q->head) {
        return false; /* Черга порожня */
    }

    *out_ev = q->buffer[current_tail];
    __asm volatile("" ::: "memory");
    q->tail = (current_tail + 1U) & EVENT_QUEUE_MASK;
    return true;
}

#endif /* EVENT_QUEUE_H */
