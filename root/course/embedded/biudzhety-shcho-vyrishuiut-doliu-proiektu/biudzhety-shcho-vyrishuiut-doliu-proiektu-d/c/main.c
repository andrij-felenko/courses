#include <stdint.h>
#include <stdbool.h>

#define TASK_COUNT_MAX 4

typedef struct {
    uint32_t flash_free_bytes;      /* Вільний запас активного банку Flash */
    uint32_t ram_heap_free_bytes;   /* Залишок динамічної кучі (Heap) */
    uint32_t task_stack_min_bytes[TASK_COUNT_MAX]; /* Вотермарка стеку задач */
    int16_t  core_temperature_c;    /* Температура кристала (°C * 10) */
    uint16_t vdd_millivolts;        /* Напруга живлення цифрової шини (мВ) */
    bool     ota_slot_available;    /* Наявність ізольованого слота під OTA */
} system_budget_audit_t;

typedef enum {
    BUDGET_STATUS_OK = 0,
    BUDGET_WARN_MEMORY_LOW,
    BUDGET_WARN_THERMAL_LIMIT,
    BUDGET_CRITICAL_VOLTAGE_SAG
} budget_status_e;

budget_status_e evaluate_system_budgets(const system_budget_audit_t *audit) {
    if (audit == 0) {
        return BUDGET_WARN_MEMORY_LOW;
    }

    /* 1. Перевірка критичного просідання живлення (BOR поріг) */
    if (audit->vdd_millivolts < 2900) {
        return BUDGET_CRITICAL_VOLTAGE_SAG;
    }

    /* 2. Перевірка теплового бюджету (максимум +85 °C для промислових МК) */
    if (audit->core_temperature_c > 850) {
        return BUDGET_WARN_THERMAL_LIMIT;
    }

    /* 3. Перевірка запасу пам'яті (Heap < 8 КБ або відсутність OTA) */
    if (audit->ram_heap_free_bytes < 8192 || !audit->ota_slot_available) {
        return BUDGET_WARN_MEMORY_LOW;
    }

    /* 4. Перевірка переповнення стеків задач (Stack Overflow Watermark) */
    for (uint32_t i = 0; i < TASK_COUNT_MAX; ++i) {
        if (audit->task_stack_min_bytes[i] < 256) {
            return BUDGET_WARN_MEMORY_LOW;
        }
    }

    return BUDGET_STATUS_OK;
}
