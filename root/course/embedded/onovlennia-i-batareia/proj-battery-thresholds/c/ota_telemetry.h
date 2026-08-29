#ifndef OTA_TELEMETRY_H
#define OTA_TELEMETRY_H

#include <stddef.h>
#include <stdint.h>

#include "battery_gate.h"

/* Відмова, надіслана серверу кампанії: код причини, вікно повтору
   й самі виміри, щоб сервер не гадав, а планував. */

typedef enum {
    OTA_RETRY_COLD        = 0x21,
    OTA_RETRY_HOT         = 0x22,
    OTA_RETRY_LOW_SOC     = 0x23,
    OTA_ALERT_HIGH_ESR    = 0x41,
    OTA_ALERT_SENSOR_FAIL = 0x42,
    OTA_ALERT_POWER_FAULT = 0x43
} ota_telemetry_code_t;

typedef struct {
    ota_telemetry_code_t code;
    uint32_t             retry_after_s;    /* 0 — повторювати немає сенсу */
    bool                 service_required; /* заводити задачу технікові */
} ota_deny_summary_t;

/* Повертає false, якщо вердикт дозвільний: телеметрії відмови немає. */
bool ota_telemetry_summarize(const ota_gate_report_t *report,
                             const ota_limits_t *lim,
                             ota_deny_summary_t *out);

/* Пакує пакет у буфер. Повертає довжину або -1, якщо не вмістилось. */
int ota_telemetry_encode(const ota_gate_report_t *report,
                         const ota_limits_t *lim,
                         uint8_t *buf,
                         size_t cap);

const char *ota_telemetry_code_name(ota_telemetry_code_t code);

#endif /* OTA_TELEMETRY_H */
