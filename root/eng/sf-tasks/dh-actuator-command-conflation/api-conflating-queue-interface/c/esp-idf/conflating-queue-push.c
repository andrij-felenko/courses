#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/mcpwm.h"

// Структурний вектор команди актуатора
typedef struct {
    uint16_t pulse_width_us; // Ширина імпульсу ШІМ у мікросекундах
    uint8_t  direction;      // Напрямок обертання (0 - реверс, 1 - вперед)
} actuator_command_t;

// Слот згортання команд із атомарним прапором
typedef struct {
    actuator_command_t data;
    atomic_bool        has_new_data;
} conflating_slot_t;

static conflating_slot_t g_actuator_slot = {
    .data = { .pulse_width_us = 1500, .direction = 1 },
    .has_new_data = ATOMIC_VAR_INIT(false)
};

static TaskHandle_t g_driver_task_handle = NULL;

// Атомарне надсилання команди у чергу згортання
void conflating_queue_push(uint16_t pulse_us, uint8_t dir) {
    actuator_command_t new_cmd = {
        .pulse_width_us = pulse_us,
        .direction = dir
    };

    // Запис нової команди у слот із перезаписом застарілих даних
    g_actuator_slot.data = new_cmd;
    atomic_store_explicit(&g_actuator_slot.has_new_data, true, memory_order_release);

    // Сповіщення задачі-драйвера про наявність оновлених даних
    if (g_driver_task_handle != NULL) {
        xTaskNotifyGive(g_driver_task_handle);
    }
}

// Застосування команди безпосередньо до апаратних регістрів ШІМ
static inline void actuator_commit_hardware(const actuator_command_t *cmd) {
    // Встановлення прямого значення у регістр порівняння таймера
    mcpwm_set_duty_in_us(MCPWM_UNIT_0, MCPWM_TIMER_0, MCPWM_OPR_A, cmd->pulse_width_us);
}

// Задача-драйвер актуатора
void actuator_driver_task(void *pvParameters) {
    (void)pvParameters;
    actuator_command_t current_cmd;

    for (;;) {
        // Очікування сповіщення від виробника команд
        ulTaskNotifyTake(pdTRUE, portMAX_DELAY);

        // Атомарна перевірка та вилучення найновішої команди
        if (atomic_exchange_explicit(&g_actuator_slot.has_new_data, false, memory_order_acq_rel)) {
            current_cmd = g_actuator_slot.data;

            // Валідація граничних значень перед записом у регістри
            if (current_cmd.pulse_width_us < 1000) current_cmd.pulse_width_us = 1000;
            if (current_cmd.pulse_width_us > 2000) current_cmd.pulse_width_us = 2000;

            actuator_commit_hardware(&current_cmd);
        }
    }
}
