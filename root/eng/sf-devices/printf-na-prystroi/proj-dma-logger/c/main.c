#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>
#include <stdarg.h>
#include <stdio.h>

#define UART_LOG_BUFFER_SIZE 2048U
#define UART_LOG_BUFFER_MASK (UART_LOG_BUFFER_SIZE - 1U)

typedef struct {
    uint8_t buffer[UART_LOG_BUFFER_SIZE];
    volatile size_t head;            /* Позиція запису ядром */
    volatile size_t tail;            /* Позиція читання DMA */
    volatile size_t dma_active_len;  /* Кількість байтів у поточній транзакції DMA */
    volatile bool dma_busy;          /* Прапорець активної передачі */
    volatile uint32_t dropped_bytes; /* Лічильник втрачених байтів при переповненні */
} async_logger_t;

static async_logger_t g_logger;

/* Апаратні функції запуску та синхронізації (адаптуються під конкретний MCU) */
extern void hw_uart_dma_start_transfer(const uint8_t *src, size_t length);
extern void hw_enter_critical(void);
extern void hw_exit_critical(void);
extern void hw_dcache_clean_range(const void *addr, size_t size);

void async_logger_init(void) {
    g_logger.head = 0;
    g_logger.tail = 0;
    g_logger.dma_active_len = 0;
    g_logger.dma_busy = false;
    g_logger.dropped_bytes = 0;
}

static size_t async_logger_available_space(void) {
    size_t head = g_logger.head;
    size_t tail = g_logger.tail;
    if (head >= tail) {
        return (UART_LOG_BUFFER_SIZE - 1U) - (head - tail);
    }
    return (tail - head) - 1U;
}

static void async_logger_kick_dma_locked(void) {
    if (g_logger.dma_busy) {
        return;
    }
    if (g_logger.head == g_logger.tail) {
        return; /* Буфер порожній */
    }

    size_t chunk_len;
    if (g_logger.head > g_logger.tail) {
        chunk_len = g_logger.head - g_logger.tail;
    } else {
        /* Передача до фізичного кінця масиву */
        chunk_len = UART_LOG_BUFFER_SIZE - g_logger.tail;
    }

    g_logger.dma_busy = true;
    g_logger.dma_active_len = chunk_len;

    /* Скидання кешу даних перед стартом читання контролером DMA */
    hw_dcache_clean_range(&g_logger.buffer[g_logger.tail], chunk_len);
    hw_uart_dma_start_transfer(&g_logger.buffer[g_logger.tail], chunk_len);
}

size_t async_logger_write(const uint8_t *data, size_t len) {
    if (data == NULL || len == 0) {
        return 0;
    }

    hw_enter_critical();

    size_t free_space = async_logger_available_space();
    if (len > free_space) {
        /* При переповненні відкидаємо надлишок і фіксуємо втрату */
        g_logger.dropped_bytes += (uint32_t)(len - free_space);
        len = free_space;
    }

    if (len == 0) {
        hw_exit_critical();
        return 0;
    }

    size_t current_head = g_logger.head;
    size_t first_part = UART_LOG_BUFFER_SIZE - current_head;

    if (len <= first_part) {
        memcpy(&g_logger.buffer[current_head], data, len);
        g_logger.head = (current_head + len) & UART_LOG_BUFFER_MASK;
    } else {
        memcpy(&g_logger.buffer[current_head], data, first_part);
        memcpy(&g_logger.buffer[0], data + first_part, len - first_part);
        g_logger.head = (len - first_part) & UART_LOG_BUFFER_MASK;
    }

    async_logger_kick_dma_locked();

    hw_exit_critical();
    return len;
}

int async_logger_printf(const char *fmt, ...) {
    char temp_staging[128];
    va_list args;
    va_start(args, fmt);
    int len = vsnprintf(temp_staging, sizeof(temp_staging), fmt, args);
    va_end(args);

    if (len > 0) {
        size_t to_write = ((size_t)len < sizeof(temp_staging)) ? (size_t)len : (sizeof(temp_staging) - 1U);
        async_logger_write((const uint8_t*)temp_staging, to_write);
    }
    return len;
}

/* Обробник переривання DMA Transfer Complete (ISR) */
void async_logger_dma_isr_handler(void) {
    /* Оновлюємо хвіст буфера на довжину відправленої пачки */
    g_logger.tail = (g_logger.tail + g_logger.dma_active_len) & UART_LOG_BUFFER_MASK;
    g_logger.dma_active_len = 0;
    g_logger.dma_busy = false;

    /* Запускаємо наступний фрагмент, якщо в буфері лишилися дані */
    async_logger_kick_dma_locked();
}
