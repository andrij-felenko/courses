#include <stdio.h>
#include <stdbool.h>
#include "roll_analysis.h"

int main(void) {
    printf("=== Аналіз масивів вибірок осцилограми у режимі Roll Mode ===\n\n");

    /* 1. Симуляція масиву вибірок пускового перехідного процесу (наприклад, запуск джерела живлення) */
    roll_sample_t startup_samples[] = {
        { .timestamp_sec = 0.0, .voltage_v = 0.0 },
        { .timestamp_sec = 0.5, .voltage_v = 7.2 },  /* Перерегулювання */
        { .timestamp_sec = 1.0, .voltage_v = 3.8 },  /* Просідання */
        { .timestamp_sec = 1.5, .voltage_v = 5.4 },  /* Невеличкий викид поза 5% коридор */
        { .timestamp_sec = 2.0, .voltage_v = 5.08 }, /* Вхід у 5% коридор (4.75 В .. 5.25 В) */
        { .timestamp_sec = 2.5, .voltage_v = 4.97 },
        { .timestamp_sec = 3.0, .voltage_v = 5.01 }
    };
    size_t startup_count = sizeof(startup_samples) / sizeof(startup_samples[0]);

    double target_voltage = 5.0; /* Усталена напруга 5.0 В */
    double tolerance_pct = 5.0;  /* 5% допускний коридор */

    transient_result_t trans_res = calculate_transient_duration(
        startup_samples,
        startup_count,
        target_voltage,
        tolerance_pct
    );

    if (trans_res.is_valid) {
        printf("[1] Пусковий перехідний процес:\n");
        printf("    Усталена напруга: %.2f В (допуск ±%.1f%%)\n", trans_res.steady_voltage_v, tolerance_pct);
        printf("    Тривалість перехідного процесу (Δt): %.2f с\n\n", trans_res.transient_time_sec);
    } else {
        printf("[1] Помилка обчислення пускового процесу.\n\n");
    }

    /* 2. Симуляція оцінки розряду акумулятора за двома курсорними відліками */
    roll_cursors_t battery_cursors = {
        .t1 = { .timestamp_sec = 10.0, .voltage_v = 4.10 }, /* Курсор 1 */
        .t2 = { .timestamp_sec = 70.0, .voltage_v = 3.95 }  /* Курсор 2 через 60 секунд */
    };
    double cutoff_voltage = 3.30; /* Напруга відсічки розрядженого літієвого акумулятора */

    discharge_result_t disch_res = estimate_battery_discharge_time(
        &battery_cursors,
        cutoff_voltage
    );

    if (disch_res.is_valid) {
        double dt_cursors = battery_cursors.t2.timestamp_sec - battery_cursors.t1.timestamp_sec;
        double dv_cursors = battery_cursors.t2.voltage_v - battery_cursors.t1.voltage_v;

        printf("[2] Оцінка часу розряду акумулятора:\n");
        printf("    Інтервал курсорів Δt: %.1f с, ΔV: %.3f В\n", dt_cursors, dv_cursors);
        printf("    Швидкість падіння напруги (dV/dt): %.5f В/с\n", disch_res.discharge_rate_v_per_s);
        printf("    Прогнозований залишковий час до відсічки (%.2f В): %.1f с (%.2f хв)\n",
               cutoff_voltage, disch_res.remaining_time_sec, disch_res.remaining_time_sec / 60.0);
    } else {
        printf("[2] Помилка аналізу курсорних відліків акумулятора.\n");
    }

    return 0;
}
