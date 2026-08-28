#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define WDT_MAX_TASKS          8
#define WDT_MAGIC_VALID        0x5A5AA5A5U
#define WDT_CHECKPOINT_FINAL   0x3C69A55AU

typedef struct {
    uint32_t task_id;
    uint32_t timeout_ms;
    uint32_t last_checkin_tick;
    uint32_t expected_checkpoint;
    uint32_t current_checkpoint;
    bool is_registered;
    bool is_active;
} wdt_task_entry_t;

// Діагностичний блок у незатертій секції RAM (.noinit)
typedef struct {
    uint32_t magic;
    uint32_t fault_task_id;
    uint32_t fault_tick;
    uint32_t fault_reason; // 1 = Timeout, 2 = Checkpoint error
} wdt_crash_dump_t;

__attribute__((section(".noinit"))) static volatile wdt_crash_dump_t g_crash_dump;

static wdt_task_entry_t g_tasks[WDT_MAX_TASKS];
static uint32_t g_registered_count = 0;

// Апаратна функція скидання конкретного WDT (наприклад IWDG)
static inline void hw_watchdog_reload(void) {
    // Для STM32: IWDG->KR = 0x0000AAAAU;
    volatile uint32_t *iwdg_kr = (volatile uint32_t *)0x40003000U;
    *iwdg_kr = 0xAAAAU;
}

// Отримання системного часу в мілісекундах
extern uint32_t sys_get_tick_ms(void);

bool wdt_supervisor_init(void) {
    for (size_t i = 0; i < WDT_MAX_TASKS; ++i) {
        g_tasks[i].is_registered = false;
        g_tasks[i].is_active = false;
    }
    g_registered_count = 0;
    return true;
}

int32_t wdt_register_task(uint32_t task_id, uint32_t timeout_ms) {
    if (g_registered_count >= WDT_MAX_TASKS) {
        return -1;
    }
    for (size_t i = 0; i < g_registered_count; ++i) {
        if (g_tasks[i].task_id == task_id) {
            return (int32_t)i; // Вже зареєстровано
        }
    }
    size_t idx = g_registered_count++;
    g_tasks[idx].task_id = task_id;
    g_tasks[idx].timeout_ms = timeout_ms;
    g_tasks[idx].last_checkin_tick = sys_get_tick_ms();
    g_tasks[idx].expected_checkpoint = WDT_CHECKPOINT_FINAL;
    g_tasks[idx].current_checkpoint = WDT_CHECKPOINT_FINAL;
    g_tasks[idx].is_registered = true;
    g_tasks[idx].is_active = true;
    return (int32_t)idx;
}

void wdt_task_checkpoint(uint32_t task_handle, uint32_t phase_step) {
    if (task_handle >= g_registered_count || !g_tasks[task_handle].is_active) {
        return;
    }
    // Оновлюємо хеш контрольних точок: перестановка бітів + фазовий крок
    uint32_t cp = g_tasks[task_handle].current_checkpoint;
    g_tasks[task_handle].current_checkpoint = (cp << 3) ^ (cp >> 29) ^ phase_step;
}

void wdt_task_checkin(uint32_t task_handle) {
    if (task_handle >= g_registered_count || !g_tasks[task_handle].is_active) {
        return;
    }
    // Атомарно фіксуємо час оновлення
    g_tasks[task_handle].last_checkin_tick = sys_get_tick_ms();
    g_tasks[task_handle].current_checkpoint = WDT_CHECKPOINT_FINAL;
}

bool wdt_supervisor_process(void) {
    uint32_t now = sys_get_tick_ms();

    for (size_t i = 0; i < g_registered_count; ++i) {
        if (!g_tasks[i].is_active) {
            continue;
        }

        // 1. Перевірка таймауту виконання
        uint32_t elapsed = now - g_tasks[i].last_checkin_tick;
        if (elapsed > g_tasks[i].timeout_ms) {
            // Зависання задачі: зберігаємо діагностику та зупиняємо оновлення WDT
            g_crash_dump.magic = WDT_MAGIC_VALID;
            g_crash_dump.fault_task_id = g_tasks[i].task_id;
            g_crash_dump.fault_tick = now;
            g_crash_dump.fault_reason = 1; // Timeout
            return false; // НЕ скидаємо апаратний WDT
        }

        // 2. Перевірка контрольної точки
        if (g_tasks[i].current_checkpoint != g_tasks[i].expected_checkpoint) {
            g_crash_dump.magic = WDT_MAGIC_VALID;
            g_crash_dump.fault_task_id = g_tasks[i].task_id;
            g_crash_dump.fault_tick = now;
            g_crash_dump.fault_reason = 2; // Bad Checkpoint
            return false;
        }
    }

    // Усі задачі здорові — скидаємо апаратний сторож
    hw_watchdog_reload();
    return true;
}

bool wdt_get_crash_report(wdt_crash_dump_t *out_report) {
    if (g_crash_dump.magic == WDT_MAGIC_VALID) {
        *out_report = g_crash_dump;
        g_crash_dump.magic = 0; // Очищуємо після зчитування
        return true;
    }
    return false;
}
