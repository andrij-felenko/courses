#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdatomic.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

typedef struct {
    uint16_t setpoint;
    bool     is_emergency;
} actuator_msg_t;

typedef struct {
    actuator_msg_t slot_data;
    atomic_bool    has_data;
    atomic_uint    total_received;
    atomic_uint    total_committed;
} actuator_diag_system_t;

static actuator_diag_system_t g_diag_sys = {
    .has_data = ATOMIC_VAR_INIT(false),
    .total_received = ATOMIC_VAR_INIT(0),
    .total_committed = ATOMIC_VAR_INIT(0)
};

// Надсилання аварійного сигналу з пріоритетним обходом
void actuator_send_emergency_stop(void) {
    atomic_fetch_add(&g_diag_sys.total_received, 1);
    
    // Аварійна команда негайно перезаписує регістр та вихідний стан
    g_diag_sys.slot_data.setpoint = 0;
    g_diag_sys.slot_data.is_emergency = true;
    atomic_store(&g_diag_sys.has_data, true);
    
    // Пряме вимкнення периферійного виходу у критичній секції
    portENTER_CRITICAL();
    // TIM1->BDTR &= ~TIM_BDTR_MOE; // Апаратне блокування виходів ШІМ
    portEXIT_CRITICAL();
}

// Виконання діагностичної обробки у циклі драйвера
void actuator_diagnostic_loop_step(void) {
    if (atomic_exchange(&g_diag_sys.has_data, false)) {
        actuator_msg_t cmd = g_diag_sys.slot_data;
        atomic_fetch_add(&g_diag_sys.total_committed, 1);

        if (cmd.is_emergency) {
            // Аварійна зупинка виконавчого механізму
            // gpio_set_level(EMERGENCY_PIN, 0);
        } else {
            // Запис звичайного значення у регістр порівняння
            // TIM1->CCR1 = cmd.setpoint;
        }
    }
}

// Обчислення коефіцієнта згортання для телеметрії
float actuator_get_conflation_rate(void) {
    unsigned int rx = atomic_load(&g_diag_sys.total_received);
    unsigned int tx = atomic_load(&g_diag_sys.total_committed);
    if (rx == 0) return 0.0f;
    return (float)(rx - tx) / (float)rx;
}
