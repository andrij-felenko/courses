/* ============================================================================
 * Драйвер захисту H-моста для вбудованих систем (C99 / MISRA C compliant)
 * Забезпечує інтеграцію з таймером ШІМ і безпечне керування станами моста.
 * ============================================================================ */

#include <stdint.h>
#include <stdbool.h>

#define DESAT_MAX_RETRIES          3U
#define DESAT_COOLDOWN_PERIOD_MS   3000U

typedef enum {
    HBRIDGE_STATE_DISABLED = 0,
    HBRIDGE_STATE_NORMAL_RUN,
    HBRIDGE_STATE_FAULT_TRIPPED,
    HBRIDGE_STATE_LOCKOUT_FATAL
} hbridge_fault_state_t;

typedef struct {
    volatile hbridge_fault_state_t state;
    uint32_t fault_events_count;
    uint32_t last_fault_time_ms;
    bool auto_recovery_enabled;
} hbridge_protection_manager_t;

static hbridge_protection_manager_t g_protection_mgr = {
    .state = HBRIDGE_STATE_DISABLED,
    .fault_events_count = 0U,
    .last_fault_time_ms = 0U,
    .auto_recovery_enabled = true
};

/* Апаратний обробник переривання лінії FAULT драйвера */
void EXTI_GateDriver_Fault_IRQHandler(void)
{
    /* Вхід BKIN таймера вже апаратно заблокував виходи ШІМ на рівні регістрів.
     * Програмне завдання — зафіксувати аварійний стан. */
    g_protection_mgr.state = HBRIDGE_STATE_FAULT_TRIPPED;
    g_protection_mgr.fault_events_count++;

    extern uint32_t Platform_GetTickMs(void);
    g_protection_mgr.last_fault_time_ms = Platform_GetTickMs();

    /* Додаткове програмне вимкнення генерації ШІМ для гарантії */
    extern void Platform_Pwm_ForceDisable(void);
    Platform_Pwm_ForceDisable();
}

/* Періодичний диспетчер безпеки моста (викликається в головному циклі або RTOS-задачі) */
void HBridge_Protection_Update(uint32_t current_time_ms)
{
    if (g_protection_mgr.state != HBRIDGE_STATE_FAULT_TRIPPED) {
        return;
    }

    /* Якщо аварії повторюються надто часто — блокуємо міст назавжди */
    if (g_protection_mgr.fault_events_count >= DESAT_MAX_RETRIES) {
        g_protection_mgr.state = HBRIDGE_STATE_LOCKOUT_FATAL;
        extern void Telemetry_LogFatalError(uint32_t code);
        Telemetry_LogFatalError(0xDEAD5A70); // Код десатурації
        return;
    }

    /* Очікування інтервалу охолодження силових ключів */
    if (g_protection_mgr.auto_recovery_enabled) {
        uint32_t elapsed = current_time_ms - g_protection_mgr.last_fault_time_ms;
        if (elapsed >= DESAT_COOLDOWN_PERIOD_MS) {
            extern bool Platform_IsFaultLineHigh(void);
            /* Перевіряємо, чи зняв драйвер апаратний сигнал FAULT */
            if (Platform_IsFaultLineHigh()) {
                extern void Platform_ResetDriverLatch(void);
                Platform_ResetDriverLatch();

                g_protection_mgr.state = HBRIDGE_STATE_DISABLED;
            }
        }
    }
}
