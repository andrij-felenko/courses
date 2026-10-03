#ifndef UART_DRIVER_H
#define UART_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

/**
 * @file uart_driver.h
 * @brief Оголошення та реалізація low-level апаратного інтерфейсу UART хост-мікроконтролера.
 * 
 * Забезпечує неблокуюче асинхронне накопичення байтів з послідовного порту UART 
 * у кільцевому буфері (Ring Buffer) в контексті обробника переривань (ISR),
 * а також функції пошуку текстових маркерів відповідей AT-команд (OK, ERROR, +PINREAD).
 */

#define UART_RING_BUFFER_SIZE 512

/**
 * @brief Структура кільцевого буфера для зберігання байтів RX UART.
 * 
 * Використовує маску для швидкого циклічного переходу за умови, що розмір є ступенем двійки.
 * Змінні head та tail оголошені volatile для безпечної передачі даних між ISR та основним потоком.
 */
typedef struct {
    uint8_t buffer[UART_RING_BUFFER_SIZE];
    volatile uint16_t head;
    volatile uint16_t tail;
    volatile bool overflow;
} uart_ring_buffer_t;

/**
 * @brief Ініціалізація кільцевого буфера.
 * @param rb Вказівник на структуру кільцевого буфера.
 */
static inline void uart_ring_buffer_init(uart_ring_buffer_t *rb) {
    if (!rb) return;
    rb->head = 0;
    rb->tail = 0;
    rb->overflow = false;
    memset((void*)rb->buffer, 0, sizeof(rb->buffer));
}

/**
 * @brief Отримання кількості доступних для читання байтів у буфері.
 * @param rb Вказівник на буфер.
 * @return Кількість накопичених байтів.
 */
static inline uint16_t uart_ring_buffer_available(const uart_ring_buffer_t *rb) {
    if (!rb) return 0;
    uint16_t h = rb->head;
    uint16_t t = rb->tail;
    return (h >= t) ? (h - t) : (UART_RING_BUFFER_SIZE - t + h);
}

/**
 * @brief Запис нового байта в буфер (викликається в перериванні RX ISR).
 * @param rb Вказівник на буфер.
 * @param byte Прийнятий байт з апаратного регістру UART.
 * @return true якщо байт успішно записано, false при переповненні буфера.
 */
static inline bool uart_ring_buffer_push(uart_ring_buffer_t *rb, uint8_t byte) {
    if (!rb) return false;
    uint16_t next_head = (rb->head + 1) & (UART_RING_BUFFER_SIZE - 1);
    if (next_head == rb->tail) {
        rb->overflow = true;
        return false;
    }
    rb->buffer[rb->head] = byte;
    rb->head = next_head;
    return true;
}

/**
 * @brief Вичитання одного байта з буфера.
 * @param rb Вказівник на буфер.
 * @param byte Вказівник для збереження прочитаного байта.
 * @return true якщо байт успішно вичитано, false якщо буфер порожній.
 */
static inline bool uart_ring_buffer_pop(uart_ring_buffer_t *rb, uint8_t *byte) {
    if (!rb || !byte || rb->head == rb->tail) return false;
    *byte = rb->buffer[rb->tail];
    rb->tail = (rb->tail + 1) & (UART_RING_BUFFER_SIZE - 1);
    return true;
}

/**
 * @brief Очищення вмісту кільцевого буфера.
 * @param rb Вказівник на буфер.
 */
static inline void uart_ring_buffer_clear(uart_ring_buffer_t *rb) {
    if (!rb) return;
    rb->head = 0;
    rb->tail = 0;
    rb->overflow = false;
}

/**
 * @brief Пошук підрядка (маркера) у кільцевому буфері без видалення прочитаних даних.
 * 
 * @param rb Вказівник на буфер.
 * @param pattern Рядок-шаблон для пошуку (наприклад "OK\r\n" або "+PINREAD:").
 * @return Зміщення шаблону відносно хвоста (tail) у байтах або -1, якщо маркер не знайдено.
 */
static inline int uart_ring_buffer_find(const uart_ring_buffer_t *rb, const char *pattern) {
    if (!rb || !pattern) return -1;
    size_t pat_len = strlen(pattern);
    uint16_t avail = uart_ring_buffer_available(rb);
    if (pat_len == 0 || avail < pat_len) return -1;

    for (uint16_t i = 0; i <= avail - pat_len; i++) {
        bool match = true;
        for (size_t j = 0; j < pat_len; j++) {
            uint16_t idx = (rb->tail + i + j) & (UART_RING_BUFFER_SIZE - 1);
            if ((char)rb->buffer[idx] != pattern[j]) {
                match = false;
                break;
            }
        }
        if (match) return (int)i;
    }
    return -1;
}

/**
 * @brief Пропуск вказаної кількості байтів у буфері (зміщення хвоста).
 * @param rb Вказівник на буфер.
 * @param len Кількість байтів для пропуску.
 */
static inline void uart_ring_buffer_skip(uart_ring_buffer_t *rb, uint16_t len) {
    if (!rb) return;
    uint16_t avail = uart_ring_buffer_available(rb);
    uint16_t skip_len = (len > avail) ? avail : len;
    rb->tail = (rb->tail + skip_len) & (UART_RING_BUFFER_SIZE - 1);
}

/* Прототипи апаратного шарніру UART хост-мікроконтролера */
bool uart_init(uint32_t baudrate);
void uart_tx_bytes(const uint8_t *data, size_t length);
void uart_tx_string(const char *str);

#endif /* UART_DRIVER_H */
