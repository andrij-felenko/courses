#include <stdio.h>
#include "rvdt_driver.h"

int main(void) {
    printf("=== Драйвер розбору сигналів давача RVDT (C) ===\n\n");

    rvdt_config_t config = {
        .max_angle_deg = 45.0f,
        .sensitivity_v_v_deg = 0.025f,
        .zero_offset_deg = 0.0f,
        .min_sum_voltage_v = 0.5f,
        .max_sum_voltage_v = 15.0f,
        .alpha_filter = 0.25f
    };

    rvdt_state_t state;
    rvdt_init(&state, &config);

    // Тестовий набір вибірок АЦП (V_S1, V_S2)
    struct {
        float vs1;
        float vs2;
        const char *desc;
    } samples[] = {
        { 3.5f, 3.5f, "Нульове положення (рівні амплітуди)" },
        { 4.5f, 2.5f, "Поворот управо на +15 град." },
        { 5.5f, 1.5f, "Поворот управо на +30 град." },
        { 0.1f, 0.1f, "Аварія: обрив обмотки (низька сума)" },
        { 9.0f, 9.0f, "Аварія: коротке замикання (висока сума)" }
    };

    size_t num_samples = sizeof(samples) / sizeof(samples[0]);

    for (size_t i = 0; i < num_samples; ++i) {
        rvdt_error_t err = rvdt_process_sample(&state, &config, samples[i].vs1, samples[i].vs2);

        printf("Тест %zu: %s\n", i + 1, samples[i].desc);
        printf("  V_S1 = %.2f В, V_S2 = %.2f В | Сума = %.2f В, Різниця = %.2f В\n",
               state.v_s1, state.v_s2, state.sum_voltage, state.diff_voltage);

        if (err == RVDT_OK) {
            printf("  Кут ротора: сирий = %.2f град., відфільтрований = %.2f град.\n",
                   state.raw_angle_deg, state.filtered_angle_deg);
        } else {
            printf("  ПОМИЛКА RVDT (код 0x%02X): ", err);
            if (err & RVDT_ERR_OPEN_CIRCUIT) printf("[Обрив обмотки] ");
            if (err & RVDT_ERR_SHORT_CIRCUIT) printf("[Коротке замикання] ");
            if (err & RVDT_ERR_OUT_OF_RANGE) printf("[Вихід за межі] ");
            printf("\n");
        }
        printf("\n");
    }

    // Демонстрація калібрування нуля
    printf("--- Програмування нового механічного нуля ---\n");
    rvdt_process_sample(&state, &config, 4.0f, 3.0f);
    printf("Кут до калібрування: %.2f град.\n", state.raw_angle_deg);
    rvdt_calibrate_zero(&state, &config);
    printf("Новий зсув нуля: %.2f град.\n", config.zero_offset_deg);
    rvdt_process_sample(&state, &config, 4.0f, 3.0f);
    printf("Кут після калібрування: %.2f град.\n", state.raw_angle_deg);

    return 0;
}
