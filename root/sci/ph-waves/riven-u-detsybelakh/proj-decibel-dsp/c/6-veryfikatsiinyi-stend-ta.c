#include "decibel_dsp.h"
#include <stdio.h>

int main(void) {
    printf("=== Перевірка модуля акустичних перетворень (C99) ===\n\n");

    /* 1. Перевірка калібратора 94 дБ SPL (1.0 Па) */
    double p_cal = 1.0; /* 1.0 Па RMS */
    double spl_cal = pressure_to_spl(p_cal);
    printf("Акустичний калібратор: тиск = %.3f Па -> SPL = %.2f дБ (очікується 94.00 дБ)\n", p_cal, spl_cal);

    /* 2. Перевірка опорних напруг dBu та dBV */
    printf("+4 dBu (студійний стандарт) = %.4f В RMS\n", dbu_to_voltage(4.0));
    printf("-10 dBV (побутовий стандарт) = %.4f В RMS (%.2f dBu)\n", 
           dbv_to_voltage(-10.0), voltage_to_dbu(dbv_to_voltage(-10.0)));

    /* 3. Некогерентне підсумовування двох джерел по 80 дБ */
    double sources[2] = {80.0, 80.0};
    double total_80 = sum_noncoherent_spl(sources, 2);
    printf("Сума 80 дБ + 80 дБ = %.2f дБ (очікується 83.01 дБ)\n", total_80);

    /* 4. Тестування фільтрації A-weighting на частоті 1 кГц */
    a_weighting_filter_t a_flt;
    a_weighting_init_48k(&a_flt);

    const size_t N = 48000; /* 1 секунда при fs = 48 кГц */
    double sig_1k[N], out_1k[N];
    for (size_t i = 0; i < N; ++i) {
        sig_1k[i] = sqrt(2.0) * 1.0 * sin(2.0 * M_PI * 1000.0 * (double)i / 48000.0);
        out_1k[i] = a_weighting_process_sample(&a_flt, sig_1k[i]);
    }
    double rms_in_1k = calculate_rms(&sig_1k[4800], N - 4800);
    double rms_out_1k = calculate_rms(&out_1k[4800], N - 4800);
    printf("A-зважування на 1 кГц: Вхід RMS = %.3f Па, Вихід RMS = %.3f Па (Зсув = %+.2f дБ)\n",
           rms_in_1k, rms_out_1k, db_from_voltage_ratio(rms_out_1k, rms_in_1k));

    /* 5. Перевірка швидкого цілочисельного логарифма */
    uint32_t test_val = 1000000;
    printf("Fast log10(1000000) = %.4f (точне значення: 6.0000)\n", fast_log10_u32(test_val));

    return 0;
}
