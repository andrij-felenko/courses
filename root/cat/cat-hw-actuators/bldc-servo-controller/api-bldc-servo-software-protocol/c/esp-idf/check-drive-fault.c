#include <stdint.h>
#include <stdbool.h>

#define STATUS_FAULT_BIT       (1 << 3)
#define STATUS_WARNING_BIT     (1 << 7)
#define STATUS_TARGET_REACHED  (1 << 10)

#define ALARM_OVERCURRENT      (1 << 0)
#define ALARM_OVERVOLTAGE      (1 << 1)
#define ALARM_UNDERVOLTAGE     (1 << 2)
#define ALARM_OVERTEMP         (1 << 3)
#define ALARM_ENCODER_ERR      (1 << 4)

// Аналіз статусу приводу та повернення прапора наявності аварії
bool check_drive_fault(uint16_t statusword, uint16_t alarm_code) {
    if (statusword & STATUS_FAULT_BIT) {
        if (alarm_code & ALARM_OVERCURRENT) {
            // Обробити надструм
        }
        if (alarm_code & ALARM_OVERTEMP) {
            // Обробити перегрів MOSFET
        }
        return true; // Збій підтверджено
    }
    return false;
}

// Формування команди скидання помилки Fault Reset
uint16_t build_fault_reset_command(void) {
    // Біт 7 у Controlword викликає скидання тривоги по позитивному фронту
    return (1 << 7);
}
