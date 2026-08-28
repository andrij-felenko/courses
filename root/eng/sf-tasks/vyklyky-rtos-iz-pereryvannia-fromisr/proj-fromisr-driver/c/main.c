#include <stdint.h>
#include <stdbool.h>
#include "FreeRTOS.h"
#include "task.h"

#define UART_RING_BUFFER_SIZE 256
#define UART_RING_BUFFER_MASK (UART_RING_BUFFER_SIZE - 1)

/* Структура кільцевого буфера SPSC */
typedef struct {
    uint8_t buffer[UART_RING_BUFFER_SIZE];
    volatile uint32_t head; /* Модифікує лише ISR (Top-Half) */
    volatile uint32_t tail; /* Модифікує лише Task (Bottom-Half) */
    volatile uint32_t dropped_bytes;
} uart_ring_buffer_t;

/* Глобальний контекст драйвера */
static uart_ring_buffer_t g_uart_rb = {0};
static TaskHandle_t g_uart_worker_task_handle = NULL;

/* Фіктивна структура регістрів UART для ілюстрації */
typedef struct {
    volatile uint32_t SR;
    volatile uint32_t DR;
    volatile uint32_t CR1;
} USART_TypeDef_Mock;

#define USART_SR_RXNE (1U << 5)
#define USART_SR_ORE  (1U << 3)
extern USART_TypeDef_Mock *USART1_MOCK;

/* --- Top-Half: Апаратний обробник переривання --- */
void USART1_IRQHandler(void) {
    BaseType_t xHigherPriorityTaskWoken = pdFALSE;
    uint32_t status = USART1_MOCK->SR;

    /* Фіксація апаратної помилки переповнення вхідного регістра */
    if (status & USART_SR_ORE) {
        volatile uint32_t dummy = USART1_MOCK->DR;
        (void)dummy;
        g_uart_rb.dropped_bytes++;
    }

    /* Обробка прийнятого байта */
    if (status & USART_SR_RXNE) {
        uint8_t received_byte = (uint8_t)(USART1_MOCK->DR & 0xFF);
        uint32_t current_head = g_uart_rb.head;
        uint32_t next_head = (current_head + 1) & UART_RING_BUFFER_MASK;

        /* Перевірка наявності вільного місця в програмному кільці */
        if (next_head != g_uart_rb.tail) {
            g_uart_rb.buffer[current_head] = received_byte;
            
            /* Бар'єр пам'яті для гарантії збереження даних до оновлення індексу */
            __asm volatile ("dmb" ::: "memory");
            g_uart_rb.head = next_head;

            /* Будимо задачу-обробник через пряме сповіщення TCB */
            if (g_uart_worker_task_handle != NULL) {
                vTaskNotifyGiveFromISR(g_uart_worker_task_handle, &xHigherPriorityTaskWoken);
            }
        } else {
            /* Програмне переповнення кільцевого буфера */
            g_uart_rb.dropped_bytes++;
        }
    }

    /* Негайне відкладене витіснення на worker task через PendSV */
    portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
}

/* --- Bottom-Half: Задача-обробник протоколу --- */
void uart_worker_task(void *pvParameters) {
    (void)pvParameters;
    g_uart_worker_task_handle = xTaskGetCurrentTaskHandle();

    for (;;) {
        /* Засинаємо з нульовим використанням CPU, доки ISR не розбудить нас */
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        /* Вичитуємо всі накопичені байти з буфера в локальний масив */
        while (g_uart_rb.tail != g_uart_rb.head) {
            uint8_t byte = g_uart_rb.buffer[g_uart_rb.tail];
            
            __asm volatile ("dmb" ::: "memory");
            g_uart_rb.tail = (g_uart_rb.tail + 1) & UART_RING_BUFFER_MASK;

            /* Виклик важкої функції обробки протоколу */
            // process_protocol_byte(byte);
        }
    }
}
