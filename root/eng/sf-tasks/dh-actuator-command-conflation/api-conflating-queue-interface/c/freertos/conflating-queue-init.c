#include <stdint.h>
#include <stdbool.h>
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

#define MAX_ACTUATORS 8

/* Структура команди актуатора */
typedef struct {
    float target_position;
    float target_velocity;
    uint32_t command_flags;
} actuator_cmd_t;

/* Слот черги згортання */
typedef struct {
    actuator_cmd_t command;
    volatile bool is_pending;
} conflating_slot_t;

/* Структура черги згортання */
typedef struct {
    conflating_slot_t slots[MAX_ACTUATORS];
    TaskHandle_t driver_task_handle;
} conflating_queue_t;

static conflating_queue_t g_actuator_queue;

/* Ініціалізація черги */
void conflating_queue_init(TaskHandle_t driver_task) {
    g_actuator_queue.driver_task_handle = driver_task;
    for (int i = 0; i < MAX_ACTUATORS; i++) {
        g_actuator_queue.slots[i].is_pending = false;
    }
}

/* Відправка команди зі згортанням (безпечна для ISR) */
bool conflating_queue_push(uint8_t actuator_id, const actuator_cmd_t *cmd) {
    if (actuator_id >= MAX_ACTUATORS || cmd == NULL) {
        return false;
    }

    UBaseType_t uxSavedInterruptStatus = taskENTER_CRITICAL_FROM_ISR();

    /* Згортання: перезапис даних у слоті незалежно від того, чи була непрочитана команда */
    g_actuator_queue.slots[actuator_id].command = *cmd;
    g_actuator_queue.slots[actuator_id].is_pending = true;

    taskEXIT_CRITICAL_FROM_ISR(uxSavedInterruptStatus);

    /* Сповіщення задачі-драйвера про появу нових даних */
    if (g_actuator_queue.driver_task_handle != NULL) {
        BaseType_t xHigherPriorityTaskWoken = pdFALSE;
        vTaskNotifyGiveFromISR(g_actuator_queue.driver_task_handle, &xHigherPriorityTaskWoken);
        portYIELD_FROM_ISR(xHigherPriorityTaskWoken);
    }

    return true;
}

/* Вибірка актуальної команди драйвером */
bool conflating_queue_pop(uint8_t actuator_id, actuator_cmd_t *out_cmd) {
    if (actuator_id >= MAX_ACTUATORS || out_cmd == NULL) {
        return false;
    }

    bool has_data = false;
    taskENTER_CRITICAL();

    if (g_actuator_queue.slots[actuator_id].is_pending) {
        *out_cmd = g_actuator_queue.slots[actuator_id].command;
        g_actuator_queue.slots[actuator_id].is_pending = false;
        has_data = true;
    }

    taskEXIT_CRITICAL();
    return has_data;
}
