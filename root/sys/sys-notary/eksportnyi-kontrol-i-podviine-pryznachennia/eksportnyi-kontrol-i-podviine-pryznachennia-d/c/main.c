#include <stdint.h>
#include <stdbool.h>
#include <string.h>

// Перелік регуляторних категорій класифікації ECCN
typedef enum {
    ECCN_CATEGORY_EAR99 = 0,
    ECCN_CATEGORY_5A992_MASS_MARKET,
    ECCN_CATEGORY_5A002_DUAL_USE_CRYPTO,
    ECCN_CATEGORY_3A001_HIGH_PERF_ADC,
    ECCN_CATEGORY_7A002_PRECISION_IMU,
    ECCN_CATEGORY_MIL_SPEC_RESTRICTED
} EccnCategory;

// Структура апаратних метрик виробу для експортного аудиту
typedef struct {
    uint32_t adc_sample_rate_sps;   // Частота вибірки АЦП у семплах на секунду
    uint8_t  adc_resolution_bits;   // Розрядність АЦП у бітах
    int16_t  temp_min_celsius;      // Мінімальна робоча температура
    int16_t  temp_max_celsius;      // Максимальна робоча температура
    uint32_t crypto_key_bits;       // Довжина симетричного ключа шифрування
    bool     has_custom_crypto;     // Наявність власного криптографічного протоколу
    uint32_t imu_bias_drift_mdeg_h; // Дрейф гіроскопа (міліградуси на годину, 1000 = 1 °/год)
    uint32_t rad_hardness_krad;     // Радіаційна стійкість у кілорадах (krad Si)
} HardwareExportSpecs;

// Результат класифікації
typedef struct {
    EccnCategory category;
    const char*  eccn_code;
    bool         requires_individual_license;
} ClassificationResult;

// Функція перевірки відповідності характеристик виробу пороговим лімітам
ClassificationResult audit_hardware_export_specs(const HardwareExportSpecs* specs) {
    ClassificationResult result;
    result.category = ECCN_CATEGORY_EAR99;
    result.eccn_code = "EAR99";
    result.requires_individual_license = false;

    // 1. Перевірка радіаційної стійкості (TID >= 500 krad)
    if (specs->rad_hardness_krad >= 500) {
        result.category = ECCN_CATEGORY_MIL_SPEC_RESTRICTED;
        result.eccn_code = "3A001.a.1";
        result.requires_individual_license = true;
        return result;
    }

    // 2. Перевірка точності гіроскопа (дрейф <= 0.5 °/год -> 500 міліградусів/год)
    if (specs->imu_bias_drift_mdeg_h > 0 && specs->imu_bias_drift_mdeg_h <= 500) {
        result.category = ECCN_CATEGORY_7A002_PRECISION_IMU;
        result.eccn_code = "7A002";
        result.requires_individual_license = true;
        return result;
    }

    // 3. Перевірка параметрів АЦП (>= 1 GSPS при роздільності >= 10 біт)
    if (specs->adc_resolution_bits >= 10 && specs->adc_sample_rate_sps >= 1000000000U) {
        result.category = ECCN_CATEGORY_3A001_HIGH_PERF_ADC;
        result.eccn_code = "3A001.a.5";
        result.requires_individual_license = true;
        return result;
    }

    // 4. Перевірка розширеного військового діапазону температур (-55..+125 °C)
    if (specs->temp_min_celsius <= -55 && specs->temp_max_celsius >= 125) {
        result.category = ECCN_CATEGORY_MIL_SPEC_RESTRICTED;
        result.eccn_code = "3A001.a.2";
        result.requires_individual_license = true;
        return result;
    }

    // 5. Перевірка криптографічних засобів
    if (specs->crypto_key_bits > 56) {
        if (specs->has_custom_crypto) {
            result.category = ECCN_CATEGORY_5A002_DUAL_USE_CRYPTO;
            result.eccn_code = "5A002.a.1";
            result.requires_individual_license = true;
        } else {
            // Стандартна криптографія масового ринку згідно з приміткою Note 4
            result.category = ECCN_CATEGORY_5A992_MASS_MARKET;
            result.eccn_code = "5A992.c";
            result.requires_individual_license = false;
        }
        return result;
    }

    return result;
}
