/* test_runner.c */
#include "snubber_filter_calc.h"
#include <stdio.h>
#include <assert.h>
#include <math.h>

void test_buck_automotive_case(void) {
    printf("=== ТЕСТ 1: Автомобільний синхронний Buck 12V -> 3.3V (2.2 МГц) ===\n");
    SnubberInput in = {
        .f1_hz = 185.0e6,
        .f2_hz = 118.0e6,
        .c_test_f = 330.0e-12,
        .v_in_volts = 13.5,
        .f_sw_hz = 2.2e6,
        .cap_multiplier = 3.0
    };

    SnubberOutput out = calculate_rc_snubber(&in);
    assert(out.status == CALC_OK);
    printf("Розрахована паразитна ємність C_par:     %.2f пФ\n", out.c_par_f * 1e12);
    printf("Розрахована паразитна індуктивність L_par: %.2f нГн\n", out.l_par_h * 1e9);
    printf("Характеристичний опір Z0:                %.2f Ом\n", out.z0_ohms);
    printf("Рекомендований резистор E24:             %.2f Ом\n", out.r_snub_e24);
    printf("Рекомендований конденсатор E24:          %.2f пФ\n", out.c_snub_e24 * 1e12);
    printf("Теплові втрати на снубері:               %.3f Вт\n", out.p_loss_watts);
    printf("Піковий імпульсний струм:                %.2f А\n\n", out.i_peak_amps);

    assert(out.c_par_f > 100e-12 && out.c_par_f < 300e-12);
    assert(out.l_par_h > 2e-9 && out.l_par_h < 8e-9);
}

void test_industrial_filter_case(void) {
    printf("=== ТЕСТ 2: Промисловий вхідний фільтр 24V (500 кГц, 40 Вт) ===\n");
    FilterInput in = {
        .v_in_min_v = 18.0,
        .p_out_w = 40.0,
        .efficiency = 0.92,
        .f_sw_hz = 500.0e3,
        .v_target_att_db = 36.0,
        .l_filter_h = 4.7e-6
    };

    FilterOutput out = calculate_input_filter(&in);
    assert(out.status == CALC_OK);
    printf("Вхідний динамічний опір DC-DC:           %.2f Ом\n", out.r_in_converter);
    printf("Цільова частота зрізу f_c:               %.2f кГц\n", out.f_cutoff_ideal / 1e3);
    printf("Розрахована вихідна ємність фільтра C2:  %.2f мкФ (E24: %.2f мкФ)\n", 
           out.c_filter_ideal * 1e6, out.c_filter_e24 * 1e6);
    printf("Демпфувальна ємність Cd:                 %.2f мкФ (E12: %.2f мкФ)\n", 
           out.c_damping_ideal * 1e6, out.c_damping_e12 * 1e6);
    printf("Демпфувальний резистор Rd:               %.2f Ом (E24: %.2f Ом)\n", 
           out.r_damping_ideal, out.r_damping_e24);
    printf("Максимальний імпеданс Z_out_max:         %.2f Ом\n", out.z_out_max_ohms);
    printf("Запас стійкості Міддлбрука:              %.2f (Стійкий: %s)\n\n", 
           out.stability_margin, out.is_stable ? "ТАК" : "НІ");

    assert(out.is_stable == true);
    assert(out.stability_margin >= 3.0);
}

void test_error_boundary_cases(void) {
    printf("=== ТЕСТ 3: Перевірка граничних та аварійних умов ===\n");
    
    SnubberInput bad_freq = {
        .f1_hz = 100.0e6,
        .f2_hz = 120.0e6,
        .c_test_f = 100.0e-12,
        .v_in_volts = 12.0,
        .f_sw_hz = 500.0e3
    };
    SnubberOutput out1 = calculate_rc_snubber(&bad_freq);
    assert(out1.status == CALC_ERR_FREQ_NOT_DECREASED);
    printf("[OK] Успішно зафіксовано помилку CALC_ERR_FREQ_NOT_DECREASED\n");

    bad_freq.f2_hz = 80.0e6;
    bad_freq.c_test_f = 0.0;
    SnubberOutput out2 = calculate_rc_snubber(&bad_freq);
    assert(out2.status == CALC_ERR_INVALID_CAPACITANCE);
    printf("[OK] Успішно зафіксовано помилку CALC_ERR_INVALID_CAPACITANCE\n\n");
}

int main(void) {
    test_buck_automotive_case();
    test_industrial_filter_case();
    test_error_boundary_cases();
    printf("УСІ ТЕСТИ ПРОЙДЕНО УСПІШНО!\n");
    return 0;
}
