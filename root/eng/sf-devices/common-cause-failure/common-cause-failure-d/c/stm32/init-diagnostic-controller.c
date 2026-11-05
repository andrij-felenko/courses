#include <stdint.h>
#include <stdbool.h>

/* Стан автомата діагностики та відновлення від CCF */
typedef enum {
    SYSTEM_STATE_NOMINAL = 0,
    SYSTEM_STATE_DEGRADED_FILTERING = 1,
    SYSTEM_STATE_LIMP_HOME = 2,
    SYSTEM_STATE_SAFE_SHUTDOWN = 3
} SystemSafetyState_t;

/* Лічильники та конфігурація фільтрації збоїв */
#define GLITCH_FILTER_THRESHOLD   5U
#define FAULT_RECOVERY_LIMIT      3U

typedef struct {
    SystemSafetyState_t current_state;
    uint32_t consecutive_mismatches;
    uint32_t total_fault_events;
    uint32_t recovery_attempts;
    bool bus_recovery_triggered;
} DiagnosticController_t;

/* Ініціалізація автомата безпеки */
void init_diagnostic_controller(DiagnosticController_t *ctrl) {
    ctrl->current_state = SYSTEM_STATE_NOMINAL;
    ctrl->consecutive_mismatches = 0;
    ctrl->total_fault_events = 0;
    ctrl->recovery_attempts = 0;
    ctrl->bus_recovery_triggered = false;
}

/* Програмна процедура відновлення заблокованої шини I2C/SPI через GPIO toggling */
static void execute_i2c_bus_clear_sequence(void) {
    /* Симуляція низькорівневого скидання лінії SDA шляхом генерації 9 тактових імпульсів SCL */
    volatile uint32_t i;
    for (i = 0; i < 9; i++) {
        /* Маніпуляція виводами GPIO у режимі Open-Drain */
    }
}

/* Головний крок автомата діагностики та обробки крайових випадків */
SystemSafetyState_t process_diagnostic_event(DiagnosticController_t *ctrl, bool channel_step_valid) {
    switch (ctrl->current_state) {
        case SYSTEM_STATE_NOMINAL:
            if (!channel_step_valid) {
                ctrl->consecutive_mismatches++;
                if (ctrl->consecutive_mismatches >= GLITCH_FILTER_THRESHOLD) {
                    ctrl->current_state = SYSTEM_STATE_DEGRADED_FILTERING;
                    ctrl->total_fault_events++;
                }
            } else {
                ctrl->consecutive_mismatches = 0;
            }
            break;

        case SYSTEM_STATE_DEGRADED_FILTERING:
            if (!channel_step_valid) {
                ctrl->consecutive_mismatches++;
                if (!ctrl->bus_recovery_triggered) {
                    execute_i2c_bus_clear_sequence();
                    ctrl->bus_recovery_triggered = true;
                }
                if (ctrl->consecutive_mismatches >= (GLITCH_FILTER_THRESHOLD * 2U)) {
                    ctrl->current_state = SYSTEM_STATE_LIMP_HOME;
                }
            } else {
                /* Успішне відновлення після тимчасового збою */
                ctrl->consecutive_mismatches = 0;
                ctrl->bus_recovery_triggered = false;
                ctrl->current_state = SYSTEM_STATE_NOMINAL;
            }
            break;

        case SYSTEM_STATE_LIMP_HOME:
            if (!channel_step_valid) {
                ctrl->consecutive_mismatches++;
                if (ctrl->consecutive_mismatches >= (GLITCH_FILTER_THRESHOLD * 3U)) {
                    /* Незворотна відмова спільної причини — негайне переведення в безпечний стан */
                    ctrl->current_state = SYSTEM_STATE_SAFE_SHUTDOWN;
                }
            } else {
                /* Спроба повернення з обмеженням швидкості */
                if (ctrl->recovery_attempts < FAULT_RECOVERY_LIMIT) {
                    ctrl->recovery_attempts++;
                    ctrl->current_state = SYSTEM_STATE_DEGRADED_FILTERING;
                }
            }
            break;

        case SYSTEM_STATE_SAFE_SHUTDOWN:
        default:
            /* Блокування силового блоку: вихід можливий лише через апаратне скидання */
            ctrl->current_state = SYSTEM_STATE_SAFE_SHUTDOWN;
            break;
    }

    return ctrl->current_state;
}
