#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdio.h>

#define MAX_ECCN_LEN 16
#define MAX_REASON_LEN 64

// Типи дозволеного експортного режиму
typedef enum {
    EXPORT_MODE_NLR = 0,               // No License Required (ліцензія не потрібна)
    EXPORT_MODE_LICENSE_EXCEPTION_ENC, // Ліцензійний виняток для масової криптографії
    EXPORT_MODE_LICENSE_REQUIRED,      // Обов'язкова індивідуальна експортна ліцензія
    EXPORT_MODE_PROHIBITED_EMBARGO     // Повне ембарго / заборона експорту
} ExportMode;

// Структура вхідних апаратних та фінансових специфікацій виробу
typedef struct {
    uint32_t adc_sample_rate_sps;   // Частота вибірки АЦП (семплів на секунду)
    uint8_t  adc_resolution_bits;   // Роздільна здатність АЦП (біт)
    int16_t  temp_min_celsius;      // Мінімальна робоча температура (°C)
    int16_t  temp_max_celsius;      // Максимальна робоча температура (°C)
    uint32_t crypto_key_bits;       // Довжина симетричного ключа (біт)
    bool     has_custom_crypto;     // Наявність власного криптографічного протоколу
    uint32_t imu_bias_drift_mdeg_h; // Дрейф гіроскопа (міліградуси на годину, 500 = 0.5 °/год)
    uint32_t rad_hardness_krad;     // Радіаційна стійкість (krad Si)
    uint32_t us_origin_cost_cents;  // Вартість компонентів походженням зі США (центи)
    uint32_t total_product_cost_cents; // Повна ринкова собівартість виробу (центи)
    char     dest_country_iso[3];   // Дволітерний код країни призначення (наприклад, "DE", "UA", "IR")
    bool     is_military_end_user;  // Прапорець кінцевого військового використання
} ProductExportSpec;

// Структура підсумкового звіту класифікації
typedef struct {
    char       eccn_code[MAX_ECCN_LEN];
    ExportMode mode;
    uint8_t    de_minimis_percent;
    char       primary_control_reason[MAX_REASON_LEN];
} ExportComplianceReport;

// Перевірка списку країн під суворим ембарго
static bool is_embargoed_country(const char* iso) {
    static const char* const EMBARGO_LIST[] = {"CU", "IR", "KP", "SY", "RU", "BY"};
    const size_t list_size = sizeof(EMBARGO_LIST) / sizeof(EMBARGO_LIST[0]);
    for (size_t i = 0; i < list_size; ++i) {
        if (strncmp(iso, EMBARGO_LIST[i], 2) == 0) {
            return true;
        }
    }
    return false;
}

// Головна функція класифікації та аудиту
bool evaluate_export_compliance(const ProductExportSpec* spec, ExportComplianceReport* report) {
    if (!spec || !report) {
        return false;
    }

    memset(report, 0, sizeof(ExportComplianceReport));
    strncpy(report->eccn_code, "EAR99", MAX_ECCN_LEN - 1);
    report->mode = EXPORT_MODE_NLR;
    strncpy(report->primary_control_reason, "None (Commercial EAR99)", MAX_REASON_LEN - 1);

    // 1. Розрахунок частки De Minimis
    if (spec->total_product_cost_cents > 0) {
        uint64_t calc = ((uint64_t)spec->us_origin_cost_cents * 100ULL) / spec->total_product_cost_cents;
        report->de_minimis_percent = (calc > 100) ? 100 : (uint8_t)calc;
    }

    // 2. Аналіз технічних порогових характеристик
    if (spec->rad_hardness_krad >= 500) {
        strncpy(report->eccn_code, "3A001.a.1", MAX_ECCN_LEN - 1);
        report->mode = EXPORT_MODE_LICENSE_REQUIRED;
        strncpy(report->primary_control_reason, "Radiation Hardness >= 500 krad(Si)", MAX_REASON_LEN - 1);
    } else if (spec->imu_bias_drift_mdeg_h > 0 && spec->imu_bias_drift_mdeg_h <= 500) {
        strncpy(report->eccn_code, "7A002", MAX_ECCN_LEN - 1);
        report->mode = EXPORT_MODE_LICENSE_REQUIRED;
        strncpy(report->primary_control_reason, "Navigation-Grade Gyro Drift <= 0.5 deg/hr", MAX_REASON_LEN - 1);
    } else if (spec->adc_resolution_bits >= 10 && spec->adc_sample_rate_sps >= 1000000000U) {
        strncpy(report->eccn_code, "3A001.a.5", MAX_ECCN_LEN - 1);
        report->mode = EXPORT_MODE_LICENSE_REQUIRED;
        strncpy(report->primary_control_reason, "High-Speed ADC >= 1 GSPS at >= 10-bit", MAX_REASON_LEN - 1);
    } else if (spec->temp_min_celsius <= -55 && spec->temp_max_celsius >= 125) {
        strncpy(report->eccn_code, "3A001.a.2", MAX_ECCN_LEN - 1);
        report->mode = EXPORT_MODE_LICENSE_REQUIRED;
        strncpy(report->primary_control_reason, "Military Temp Range (-55C to +125C)", MAX_REASON_LEN - 1);
    } else if (spec->crypto_key_bits > 56) {
        if (spec->has_custom_crypto) {
            strncpy(report->eccn_code, "5A002.a.1", MAX_ECCN_LEN - 1);
            report->mode = EXPORT_MODE_LICENSE_REQUIRED;
            strncpy(report->primary_control_reason, "Dual-Use Proprietary Cryptography", MAX_REASON_LEN - 1);
        } else {
            strncpy(report->eccn_code, "5A992.c", MAX_ECCN_LEN - 1);
            report->mode = EXPORT_MODE_LICENSE_EXCEPTION_ENC;
            strncpy(report->primary_control_reason, "Mass Market Cryptography (Note 4)", MAX_REASON_LEN - 1);
        }
    }

    // 3. Перевірка країни та кінцевого використання
    if (is_embargoed_country(spec->dest_country_iso)) {
        report->mode = EXPORT_MODE_PROHIBITED_EMBARGO;
        strncpy(report->primary_control_reason, "Sanctioned/Embargoed Destination", MAX_REASON_LEN - 1);
    } else if (spec->is_military_end_user && report->mode != EXPORT_MODE_LICENSE_REQUIRED) {
        report->mode = EXPORT_MODE_LICENSE_REQUIRED;
        strncpy(report->primary_control_reason, "Military End-User (MEU) Restriction", MAX_REASON_LEN - 1);
    }

    return true;
}
