#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_CHANNELS 14
#define REG_DOMAIN_EU_ETSI 0x01
#define REG_DOMAIN_US_FCC  0x02

// Сертифікаційні ліміти, зафіксовані в Технічному файлі
typedef struct {
    uint8_t  domain_id;
    int8_t   max_tx_power_dbm;     // Максимальний допустимий рівень EIRP
    uint16_t min_freq_mhz;         // Нижня межа робочої смуги
    uint16_t max_freq_mhz;         // Верхня межа робочої смуги
    uint8_t  max_duty_cycle_pct;   // Максимальний робочий цикл (%)
    uint16_t allowed_channel_mask; // Бітова маска дозволених каналів (1..13)
} RegulatoryDomainLimits;

typedef struct {
    char     hw_revision[8];
    char     fw_version[16];
    uint8_t  active_domain;
    int8_t   configured_power_dbm;
    uint16_t current_channel_mask;
    uint32_t calibration_crc32;
} DeviceComplianceState;

// Зразок константних лімітів для ринку ЄС (ETSI EN 300 328)
static const RegulatoryDomainLimits ETSI_LIMITS = {
    .domain_id = REG_DOMAIN_EU_ETSI,
    .max_tx_power_dbm = 20,       // 100 мВт EIRP (20 dBm) для 2.4 ГГц
    .min_freq_mhz = 2400,
    .max_freq_mhz = 2483,
    .max_duty_cycle_pct = 100,
    .allowed_channel_mask = 0x1FFF // Канали 1..13 дозволені в ЄС
};

// Генератор CRC32 за стандартом IEEE 802.3
static uint32_t calculate_crc32(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFF;
    for (size_t i = 0; i < length; i++) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; j++) {
            crc = (crc >> 1) ^ (0xEDB88320 & (-(int32_t)(crc & 1)));
        }
    }
    return ~crc;
}

// Повна верифікація параметрів перед подачею живлення на передавач
bool compliance_verify_rf_parameters(const DeviceComplianceState *state,
                                     uint32_t expected_cal_crc,
                                     char *out_error_reason,
                                     size_t max_err_len) {
    if (state == NULL || out_error_reason == NULL || max_err_len == 0) {
        return false;
    }

    // 1. Контроль цілісності калібрувальних коефіцієнтів у пам'яті
    if (state->calibration_crc32 != expected_cal_crc) {
        strncpy(out_error_reason, "ERR_CALIBRATION_CRC_MISMATCH", max_err_len - 1);
        out_error_reason[max_err_len - 1] = '\0';
        return false;
    }

    // 2. Перевірка дотримання європейських регуляторних норм
    if (state->active_domain == REG_DOMAIN_EU_ETSI) {
        // Контроль перевищення еквівалентної потужності випромінювання
        if (state->configured_power_dbm > ETSI_LIMITS.max_tx_power_dbm) {
            strncpy(out_error_reason, "ERR_ETSI_TX_POWER_EXCEEDED", max_err_len - 1);
            out_error_reason[max_err_len - 1] = '\0';
            return false;
        }

        // Контроль використання заборонених частотних каналів (наприклад, канал 14)
        if ((state->current_channel_mask & ~ETSI_LIMITS.allowed_channel_mask) != 0) {
            strncpy(out_error_reason, "ERR_UNAUTHORIZED_FREQUENCY_CHANNEL", max_err_len - 1);
            out_error_reason[max_err_len - 1] = '\0';
            return false;
        }
    } else {
        strncpy(out_error_reason, "ERR_UNSUPPORTED_OR_INVALID_DOMAIN", max_err_len - 1);
        out_error_reason[max_err_len - 1] = '\0';
        return false;
    }

    out_error_reason[0] = '\0';
    return true;
}
