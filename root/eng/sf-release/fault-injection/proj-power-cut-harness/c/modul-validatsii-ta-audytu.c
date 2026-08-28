#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

typedef enum {
    VERDICT_OK_RECOVERED,
    VERDICT_BRICKED_BOOTLOOP,
    VERDICT_SILENT_CORRUPTION,
    VERDICT_TIMEOUT_NO_RESPONSE
} test_verdict_t;

typedef struct {
    uint32_t run_index;
    uint32_t cut_delay_us;
    test_verdict_t verdict;
    char details[128];
} audit_record_t;

/* Парсер виводу діагностичної консолі цільового пристрою */
test_verdict_t audit_target_console_log(const char *log_buffer, size_t length, audit_record_t *record) {
    if (length == 0 || log_buffer == NULL) {
        record->verdict = VERDICT_TIMEOUT_NO_RESPONSE;
        snprintf(record->details, sizeof(record->details), "DUT не відповів на запит завантаження");
        return VERDICT_TIMEOUT_NO_RESPONSE;
    }

    /* Перевірка на фатальні паніки ядра */
    if (strstr(log_buffer, "HardFault_Handler") != NULL || strstr(log_buffer, "PANIC:") != NULL) {
        record->verdict = VERDICT_BRICKED_BOOTLOOP;
        snprintf(record->details, sizeof(record->details), "Виявлено паніку ядра під час старту");
        return VERDICT_BRICKED_BOOTLOOP;
    }

    /* Перевірка цілісності LittleFS */
    if (strstr(log_buffer, "lfs_mount: corrupt") != NULL) {
        record->verdict = VERDICT_SILENT_CORRUPTION;
        snprintf(record->details, sizeof(record->details), "Пошкодження суперблоку файлової системи");
        return VERDICT_SILENT_CORRUPTION;
    }

    /* Перевірка успішного старту та валідного відкату */
    if (strstr(log_buffer, "BOOT_OK") != NULL || strstr(log_buffer, "ROLLBACK_OK") != NULL) {
        record->verdict = VERDICT_OK_RECOVERED;
        snprintf(record->details, sizeof(record->details), "Успішне відновлення або відкат");
        return VERDICT_OK_RECOVERED;
    }

    record->verdict = VERDICT_SILENT_CORRUPTION;
    snprintf(record->details, sizeof(record->details), "Невідомий стан цілі після рестарту");
    return VERDICT_SILENT_CORRUPTION;
}
