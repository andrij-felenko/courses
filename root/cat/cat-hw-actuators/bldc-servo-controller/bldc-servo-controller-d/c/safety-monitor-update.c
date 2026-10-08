#include <stdbool.h>

#define U_BUS_BRAKE_ON   56.0f  // Вольт
#define U_BUS_BRAKE_OFF  53.0f  // Вольт
#define U_BUS_MAX_FAULT  60.0f  // Вольт
#define TEMP_MAX_FAULT   105.0f // Градуси Цельсія

typedef struct {
    float u_bus;
    float temp_celsius;
    bool brake_chopper_active;
    bool fault_overvoltage;
    bool fault_overtemp;
    bool system_enabled;
} SafetyMonitor;

// Функція перевірки безпеки, що викликається в перериванні ШІМ
void safety_monitor_update(SafetyMonitor *mon) {
    // 1. Управління Brake Chopper (гальмівним переривачем)
    if (mon->u_bus >= U_BUS_BRAKE_ON) {
        mon->brake_chopper_active = true; // Увімкнути ключ гальмівного резистора
    } else if (mon->u_bus <= U_BUS_BRAKE_OFF) {
        mon->brake_chopper_active = false; // Вимкнути ключ
    }

    // 2. Апаратні захисти (Fault Shutdown)
    if (mon->u_bus >= U_BUS_MAX_FAULT) {
        mon->fault_overvoltage = true;
        mon->system_enabled = false; // Відключити силовий міст (High-Z)
    }

    if (mon->temp_celsius >= TEMP_MAX_FAULT) {
        mon->fault_overtemp = true;
        mon->system_enabled = false; // Відключити силовий міст (High-Z)
    }
}
