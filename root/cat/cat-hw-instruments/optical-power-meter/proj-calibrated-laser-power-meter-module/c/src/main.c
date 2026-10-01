#include <stdio.h>
#include "opm_sensor.h"

int main(void) {
    printf("=== Драйвер вимірювача оптичної потужності лазерного випромінювання (C) ===\n\n");

    /* Калібрувальна таблиця Si-фотодіода */
    static const opm_calib_point_t si_calib_points[] = {
        { 650, 0.42f },
        { 780, 0.53f },
        { 850, 0.58f },
        { 980, 0.62f },
        { 1064, 0.25f }
    };

    opm_calib_table_t calib_table = {
        .points = si_calib_points,
        .count = sizeof(si_calib_points) / sizeof(si_calib_points[0])
    };

    /* Апаратна конфігурація: Rf = 100 кОм, Vref = 3.3В, 12-біт АЦП, LIDT = 100 мВт */
    opm_config_t config = {
        .tia_gain_ohm = 100000.0f,
        .adc_vref_v = 3.3f,
        .adc_max_count = 4095,
        .lidt_max_power_w = 0.100f
    };

    opm_sensor_t sensor;
    opm_status_t status = opm_init(&sensor, &config, &calib_table);
    if (status != OPM_OK) {
        printf("Помилка ініціалізації OPM сенсора!\n");
        return 1;
    }

    printf("1. Процедура калібрування темнового струму (Zeroing)...\n");
    uint16_t dark_samples[8] = { 12, 14, 11, 13, 12, 15, 13, 12 };
    opm_calibrate_dark_offset(&sensor, dark_samples, 8);
    printf("   Темновий зсув напруги: %.4f мВ\n\n", sensor.dark_offset_v * 1000.0f);

    printf("2. Налаштування робочої довжини хвилі λ = 850 нм...\n");
    status = opm_set_wavelength(&sensor, 850);
    if (status == OPM_OK) {
        printf("   Інтерпольована чутливість R(850нм) = %.3f А/Вт\n\n", sensor.current_sensitivity_a_w);
    }

    printf("3. Імітація вимірювального циклу зняття відліків АЦП:\n");
    uint16_t test_adc_samples[] = { 150, 450, 1200, 2500, 4050 };

    for (size_t i = 0; i < sizeof(test_adc_samples) / sizeof(test_adc_samples[0]); i++) {
        float power_w = 0.0f;
        float power_dbm = 0.0f;
        
        status = opm_process_adc_sample(&sensor, test_adc_samples[i], &power_w, &power_dbm);

        printf("   [АЦП: %4u] -> Потужність: %8.3f мкВт | %6.2f dBm", 
               test_adc_samples[i], power_w * 1e6f, power_dbm);

        if (status == OPM_ERR_LIDT_EXCEEDED) {
            printf("  [УВАГА: Перевищено поріг LIDT!]\n");
        } else {
            printf("\n");
        }
    }

    return 0;
}
