#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"
#include <stdbool.h>
#include <stdint.h>

#define BUFFER_SIZE 64

typedef struct {
    uint8_t data[BUFFER_SIZE];
    uint32_t head;
    uint32_t tail;
} safe_ring_buffer_t;

static safe_ring_buffer_t g_system_buffer;

/* Додавання елемента з контексту задачі */
bool safe_buffer_push_from_task(safe_ring_buffer_t *buf, uint8_t val) {
    bool status = false;

    /* Вхід у критичну секцію задачі: маскування переривань до configMAX_SYSCALL_INTERRUPT_PRIORITY */
    taskENTER_CRITICAL();
    
    uint32_t next_head = (buf->head + 1) % BUFFER_SIZE;
    if (next_head != buf->tail) {
        buf->data[buf->head] = val;
        buf->head = next_head;
        status = true;
    }
    
    /* Вихід із критичної секції задачі */
    taskEXIT_CRITICAL();

    return status;
}

/* Додавання елемента з контексту обробника переривання (ISR) */
bool safe_buffer_push_from_isr(safe_ring_buffer_t *buf, uint8_t val) {
    bool status = false;

    /* Збереження стану переривань та встановлення маски BASEPRI */
    UBaseType_t uxSavedInterruptStatus = taskENTER_CRITICAL_FROM_ISR();

    uint32_t next_head = (buf->head + 1) % BUFFER_SIZE;
    if (next_head != buf->tail) {
        buf->data[buf->head] = val;
        buf->head = next_head;
        status = true;
    }

    /* Відновлення попереднього стану маски переривань */
    taskEXIT_CRITICAL_FROM_ISR(uxSavedInterruptStatus);

    return status;
}
