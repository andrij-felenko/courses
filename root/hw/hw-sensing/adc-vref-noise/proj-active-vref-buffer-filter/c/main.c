#include <stdio.h>
#include "vref_settling_sim.h"

int main(void)
{
    printf("=== МОДЕЛЮВАННЯ ДИНАМІЧНОГО ВСТАНОВЛЕННЯ VREF ДЛЯ SAR АЦП ===\n\n");

    /* 1. Налаштування параметрів буфера на прецизійному ОП */
    vref_buffer_config_t buffer_cfg = {
        .vref_nominal_v = 5.0,        /* 5.0 В опорна напруга */
        .gbw_hz = 20.0e6,             /* 20 МГц смуга одиничного підсилення */
        .r_out_open_loop = 50.0,      /* 50 Ом вихідний опір ОП без зворотного зв'язку */
        .c_filt_f = 10.0e-6,          /* 10 мкФ керамічний конденсатор фільтра X7R */
        .esr_c_filt_ohm = 0.015,      /* 15 мОм ESR конденсатора */
        .r_iso_ohm = 2.2,             /* 2.2 Ом ізолюючий резистор in-loop компенсації */
        .c_feedback_f = 10.0e-9       /* 10 нФ конденсатор прямого зворотного зв'язку */
    };

    /* 2. Налаштування комутації матриці CDAC 16-розрядного перетворювача */
    cdac_switch_event_t cdac_event = {
        .resolution_bits = 16,        /* 16 бітів */
        .c_sample_f = 40.0e-12,       /* 40 пФ сумарна ємність матриці вибірки */
        .v_step_v = 2.5,              /* Стрибок напруги при комутації старшого розряду MSB */
        .t_settle_budget_s = 250.0e-9 /* 250 нс тривалість такту прийняття рішення біта */
    };

    /* 3. Запуск чисельного моделювання */
    vref_sim_result_t result = {0};
    double dt_s = 1.0e-10; /* Крок інтегрування 100 пс */

    if (!vref_simulate_cdac_settling(&buffer_cfg, &cdac_event, dt_s, &result)) {
        fprintf(stderr, "Помилка: невірні вхідні параметри симуляції!\n");
        return 1;
    }

    /* 4. Виведення інженерних результатів */
    double lsb_uv = (buffer_cfg.vref_nominal_v / 65536.0) * 1.0e6;
    printf("Розрядність АЦП:             %u бітів (LSB = %.2f мкВ)\n", cdac_event.resolution_bits, lsb_uv);
    printf("Ємність буферного фільтра:    %.1f мкФ (ESR = %.1f мОм)\n", buffer_cfg.c_filt_f * 1.0e6, buffer_cfg.esr_c_filt_ohm * 1000.0);
    printf("Максимальне просідання VREF:  %.3f мВ\n", result.max_voltage_drop_v * 1000.0);
    printf("Залишкова похибка в кінці:   %.3f мкВ\n", result.residual_error_v * 1.0e6);
    printf("Похибка перетворення:        %.3f LSB\n", result.error_lsb);
    printf("Фазовий запас буфера:        %.1f градусів\n", result.phase_margin_deg);
    printf("Критерій точності (<= 0.5 LSB): %s\n", result.is_settled_within_half_lsb ? "ВИКОНАНО" : "НЕ ВИКОНАНО");

    if (result.phase_margin_deg < 45.0) {
        printf("\nУВАГА: Фазовий запас менше 45 градусів! Ризик автоколивань буфера VREF.\n");
    } else {
        printf("\nСТАТУС: Буфер VREF стабільний, динамічне встановлення відповідає вимогам 16 бітів.\n");
    }

    return 0;
}
