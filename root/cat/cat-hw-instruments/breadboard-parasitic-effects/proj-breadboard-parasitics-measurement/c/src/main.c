#include "oscilloscope_trace.h"
#include "breadboard_parasitics.h"

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>

/**
 * @brief Лінійний конгруентний генератор псевдовипадкових чисел (0.0 .. 1.0).
 */
static double lcg_uniform(uint32_t *state) {
    *state = (*state * 1664525u + 1013904223u);
    return (double)(*state) / 4294967296.0;
}

/**
 * @brief Генерація гауссового шуму методом перетворення Бокса-Мюллера.
 */
static double generate_gaussian_noise(double mean, double stddev, uint32_t *rng_state) {
    double u1 = lcg_uniform(rng_state);
    double u2 = lcg_uniform(rng_state);
    while (u1 <= 1.0e-9) {
        u1 = lcg_uniform(rng_state);
    }
    const double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * 3.14159265358979323846 * u2);
    return mean + z0 * stddev;
}

/**
 * @brief Генерація змодельованої осцилограми перехідного процесу заряджання ємності через опір (RC-ланцюг).
 *
 * Модель сигналу: v(t) = v_start + (v_final - v_start) * (1 - exp(-(t - t_step) / tau)) + шум
 */
static bool generate_rc_step_trace(oscilloscope_trace_t *trace,
                                   double v_start,
                                   double v_final,
                                   double r_ohm,
                                   double c_total_f,
                                   double step_time_s,
                                   double duration_s,
                                   double sample_interval_s,
                                   uint32_t *rng_state) {
    if (!trace) {
        return false;
    }
    trace_clear(trace);
    const double tau = r_ohm * c_total_f;

    for (double t = 0.0; t <= duration_s; t += sample_interval_s) {
        double v = v_start;
        if (t >= step_time_s) {
            const double dt = t - step_time_s;
            v = v_start + (v_final - v_start) * (1.0 - exp(-dt / tau));
        }
        v += generate_gaussian_noise(0.0, 0.003, rng_state); /* Невеликий шум АЦП (3 мВ СКО) */
        if (!trace_add_sample(trace, t, v)) {
            return false;
        }
    }

    return true;
}

/**
 * @brief Генерація змодельованої осцилограми падіння напруги на контакті під час імпульсу навантаження.
 *
 * Модель сигналу: у стані спокою напруга V_supply, під час імпульсу струму I_load
 * напруга просідає на величину Delta_V = I_load * R_contact.
 */
static bool generate_load_pulse_trace(oscilloscope_trace_t *trace,
                                      double v_supply,
                                      double r_contact_ohm,
                                      double i_load_a,
                                      double pulse_start_s,
                                      double pulse_duration_s,
                                      double duration_s,
                                      double sample_interval_s,
                                      uint32_t *rng_state) {
    if (!trace) {
        return false;
    }
    trace_clear(trace);
    const double pulse_end_s = pulse_start_s + pulse_duration_s;
    const double v_drop = i_load_a * r_contact_ohm;

    for (double t = 0.0; t <= duration_s; t += sample_interval_s) {
        double v = v_supply;
        if (t >= pulse_start_s && t <= pulse_end_s) {
            v = v_supply - v_drop;
        }
        v += generate_gaussian_noise(0.0, 0.002, rng_state); /* Шум вимірювання 2 мВ */
        if (!trace_add_sample(trace, t, v)) {
            return false;
        }
    }

    return true;
}

/**
 * @brief Форматоване виведення результатів діагностичного звіту в консоль.
 */
static void print_report(const char *title, const parasitic_report_t *rep) {
    printf("======================================================================\n");
    printf("  %s\n", title);
    printf("======================================================================\n");
    printf("  Час наростання фронту (t_r 10%%-90%%):    %8.2f нс\n", rep->rise_time_ns);
    printf("  Повна виміряна ємність (C_total):        %8.2f пФ\n", rep->total_capacitance_pf);
    printf("  Паразитна міжрейкова ємність (C_par):    %8.2f пФ\n", rep->parasitic_capacitance_pf);
    printf("  Гранична частота зрізу RC (f_-3dB):      %8.2f МГц\n", rep->cutoff_frequency_mhz);
    printf("  Падіння напруги під навантаженням:       %8.2f мВ\n", rep->voltage_drop_mv);
    printf("  Контактний перехідний опір (R_cont):     %8.2f мОм\n", rep->contact_resistance_mohm);
    printf("  Стан пружинного затискача:               %s\n", contact_health_to_string(rep->health));
    printf("----------------------------------------------------------------------\n");
    printf("  Інженерний висновок:\n  %s\n", rep->notes);
    printf("======================================================================\n\n");
}

int main(void) {
    printf("\n");
    printf("======================================================================\n");
    printf("   ДІАГНОСТИКА ПАРАЗИТНИХ ЕФЕКТІВ БЕЗПАЯЛЬНИХ МАКЕТНИХ ПЛАТ (C)\n");
    printf("   Визначення міжрейкової ємності та контактного опору за осцилограмами\n");
    printf("======================================================================\n\n");

    /*
     * Налаштування вимірювального стенда:
     * - Тестовий резистор: R_test = 10 кОм (10000 Ом) для створення вимірюваного RC-перехідного процесу
     * - Власна вхідна ємність щупа осцилографа: C_probe = 12.0 пФ (стандартний пасивний щуп 10X)
     * - Тестовий струм навантаження для імпульсного заміру опору: I_test = 0.5 А
     */
    test_bench_config_t bench_cfg;
    bench_cfg.test_resistance_ohm = 10000.0;
    bench_cfg.probe_capacitance_f = 12.0e-12;
    bench_cfg.test_load_current_a = 0.5;

    printf("Параметри вимірювального стенда:\n");
    printf(" - Опір тестового резистора (R_test):    %.1f Ом\n", bench_cfg.test_resistance_ohm);
    printf(" - Власна ємність щупа (C_probe 10X):     %.1f пФ\n", bench_cfg.probe_capacitance_f * 1.0e12);
    printf(" - Струм імпульсного навантаження:       %.1f А\n\n", bench_cfg.test_load_current_a);

    /* Ініціалізація динамічних буферів осцилограм */
    oscilloscope_trace_t step_trace;
    oscilloscope_trace_t load_trace;
    if (!trace_init(&step_trace, 2048) || !trace_init(&load_trace, 2048)) {
        fprintf(stderr, "Помилка виділення пам'яті для буферів осцилограми.\n");
        trace_free(&step_trace);
        trace_free(&load_trace);
        return 1;
    }

    /* Фіксоване початкове значення для повторюваності шуму */
    uint32_t rng_state = 42;

    /*
     * --------------------------------------------------------------------------------
     * Сценарій 1: Нова якісна макетна плата (фосфориста бронза, крок 2.54 мм)
     * Очікувані фізичні параметри:
     * - Міжрейкова паразитна ємність C_par ≈ 2.2 пФ -> Разом зі щупом C_total ≈ 14.2 пФ
     * - Контактний опір R_cont ≈ 32 мОм -> Падіння при 0.5 А складе ~16 мВ
     * --------------------------------------------------------------------------------
     */
    const double expected_c_par_1 = 2.2e-12;
    const double expected_c_total_1 = expected_c_par_1 + bench_cfg.probe_capacitance_f;
    const double expected_r_cont_1 = 0.032; /* 32 мОм */

    generate_rc_step_trace(
        &step_trace,
        0.0, 3.3, bench_cfg.test_resistance_ohm, expected_c_total_1,
        100.0e-9, 1200.0e-9, 1.0e-9, &rng_state
    );
    trace_filter_outliers(&step_trace, 1.5);

    generate_load_pulse_trace(
        &load_trace,
        5.0, expected_r_cont_1, bench_cfg.test_load_current_a,
        10.0e-6, 20.0e-6, 50.0e-6, 0.5e-6, &rng_state
    );
    trace_filter_outliers(&load_trace, 1.5);

    parasitic_report_t report_1;
    analyze_breadboard_parasitics_traces(&bench_cfg, &step_trace, &load_trace, &report_1);
    print_report("ЗРАЗОК 1: Нова якісна безпаяльна макетна плата", &report_1);

    /*
     * --------------------------------------------------------------------------------
     * Сценарій 2: Зношена / окислена дешева макетна плата
     * Очікувані фізичні параметри:
     * - Збільшена міжрейкова ємність C_par ≈ 4.8 пФ (забруднення, залишкова паста, зсув шин)
     * - Деградований контактний опір R_cont ≈ 380 мОм (втома пружинних пелюсток, окислення)
     * --------------------------------------------------------------------------------
     */
    const double expected_c_par_2 = 4.8e-12;
    const double expected_c_total_2 = expected_c_par_2 + bench_cfg.probe_capacitance_f;
    const double expected_r_cont_2 = 0.380; /* 380 мОм */

    generate_rc_step_trace(
        &step_trace,
        0.0, 3.3, bench_cfg.test_resistance_ohm, expected_c_total_2,
        100.0e-9, 1500.0e-9, 1.0e-9, &rng_state
    );
    trace_filter_outliers(&step_trace, 1.5);

    generate_load_pulse_trace(
        &load_trace,
        5.0, expected_r_cont_2, bench_cfg.test_load_current_a,
        10.0e-6, 20.0e-6, 50.0e-6, 0.5e-6, &rng_state
    );
    trace_filter_outliers(&load_trace, 1.5);

    parasitic_report_t report_2;
    analyze_breadboard_parasitics_traces(&bench_cfg, &step_trace, &load_trace, &report_2);
    print_report("ЗРАЗОК 2: Зношена / окислена макетна плата (дефектні затискачі)", &report_2);

    /* Звільнення ресурсів */
    trace_free(&step_trace);
    trace_free(&load_trace);

    /*
     * --------------------------------------------------------------------------------
     * Підсумкові інженерні висновки для макетування начорно
     * --------------------------------------------------------------------------------
     */
    printf("ПРАКТИЧНІ РЕКОМЕНДАЦІЇ ДЛЯ ІНЖЕНЕРА-РОЗРОБНИКА:\n");
    printf("1. Компенсація щупа осцилографа є критичною: ємність щупа 10X (~12 пФ)\n");
    printf("   у 4-6 разів перевищує власну ємність контактів макетки (1-3 пФ).\n");
    printf("2. Контактний опір > 200 мОм створює неприпустиме просідання шин живлення\n");
    printf("   (Delta_V = I * R) при комутації мікроконтролерів і Wi-Fi/BLE передавачів.\n");
    printf("3. Обов'язково встановлюйте керамічні блокувальні конденсатори 100 нФ\n");
    printf("   безпосередньо біля виводів живлення кожної мікросхеми на макеті.\n\n");

    return 0;
}
