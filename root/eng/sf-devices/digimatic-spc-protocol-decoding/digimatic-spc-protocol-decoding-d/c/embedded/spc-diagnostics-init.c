#include <stdint.h>
#include <stdbool.h>

typedef enum {
    SPC_OK = 0,
    SPC_ERR_TIMEOUT,
    SPC_ERR_PREAMBLE,
    SPC_ERR_BCD_RANGE,
    SPC_ERR_BATTERY_LOW,
    SPC_ERR_OVERSPEED
} spc_status_t;

typedef struct {
    uint32_t total_frames;
    uint32_t valid_frames;
    uint32_t timeout_errors;
    uint32_t preamble_errors;
    uint32_t bcd_errors;
    uint32_t battery_warnings;
    uint32_t overspeed_errors;
} spc_telemetry_t;

static spc_telemetry_t s_telemetry = {0};

void spc_diagnostics_init(void) {
    s_telemetry.total_frames = 0;
    s_telemetry.valid_frames = 0;
    s_telemetry.timeout_errors = 0;
    s_telemetry.preamble_errors = 0;
    s_telemetry.bcd_errors = 0;
    s_telemetry.battery_warnings = 0;
    s_telemetry.overspeed_errors = 0;
}

spc_status_t spc_validate_digimatic_packet(const uint8_t d[13]) {
    s_telemetry.total_frames++;

    // Перевірка індикатора розряду батареї або переповнення швидкості
    if ((d[4] & 0x04) != 0) {
        s_telemetry.battery_warnings++;
        return SPC_ERR_BATTERY_LOW;
    }

    // Перевірка преамбули 0xF 0xF 0xF 0xF
    if (d[0] != 0x0F || d[1] != 0x0F || d[2] != 0x0F || d[3] != 0x0F) {
        s_telemetry.preamble_errors++;
        return SPC_ERR_PREAMBLE;
    }

    // Перевірка коректності BCD цифр
    for (int i = 5; i <= 10; i++) {
        if (d[i] > 9) {
            s_telemetry.bcd_errors++;
            return SPC_ERR_BCD_RANGE;
        }
    }

    s_telemetry.valid_frames++;
    return SPC_OK;
}

void spc_record_timeout(void) {
    s_telemetry.total_frames++;
    s_telemetry.timeout_errors++;
}

bool spc_is_link_healthy(void) {
    if (s_telemetry.total_frames < 20) {
        return true;
    }
    uint32_t total_errors = s_telemetry.timeout_errors + s_telemetry.preamble_errors + s_telemetry.bcd_errors;
    // Канал вважається ненадійним, якщо понад 5% пакетів пошкоджено
    return (total_errors * 100 / s_telemetry.total_frames) < 5;
}
