#include <stdio.h>
#include <stdbool.h>
#include <math.h>

/* Базові фізичні константи міді */
#define COPPER_RHO_20C   1.724e-8  /* Питомий опір міді при 20°C, Ом·м */
#define COPPER_TEMP_COEF 0.00393   /* Температурний коефіцієнт опору, 1/°C */

typedef enum {
    AWG_10 = 10,
    AWG_12 = 12,
    AWG_14 = 14,
    AWG_16 = 16,
    AWG_18 = 18,
    AWG_20 = 20,
    AWG_22 = 22,
    AWG_24 = 24,
    AWG_26 = 26,
    AWG_28 = 28,
    AWG_30 = 30
} awg_gauge_t;

typedef struct {
    awg_gauge_t gauge;
    double length_m;        /* Довжина кабельної траси в один бік, метри */
    double current_amps;    /* Струм навантаження лінії, Ампери */
    double operating_temp_c;/* Очікувана температура джгута, °C */
    bool shared_ground;     /* Чи використовується зворотний провід як спільна земля */
    double bus_voltage_v;   /* Номінальна напруга живлення шини, Вольти */
} harness_spec_t;

typedef struct {
    double wire_area_mm2;       /* Площа поперечного перерізу, мм² */
    double single_wire_res_ohm; /* Опір одного провідника при робочій температурі, Ом */
    double loop_res_ohm;        /* Повний опір петлі живлення (+ та -), Ом */
    double total_voltage_drop_v;/* Сумарне падіння напруги на споживачі, В */
    double voltage_drop_percent;/* Падіння напруги у відсотках від номіналу шини */
    double ground_shift_v;      /* Зміщення потенціалу землі на боці приймача, В */
    double thermal_loss_w;      /* Потужність теплових втрат у джгуті, Вт */
    bool current_density_ok;    /* Перевірка допустимої густини струму (< 15 А/мм²) */
    bool logic_margin_ok;       /* Перевірка запасу завадостійкості (< 0.2 В для 3.3V) */
} harness_result_t;

/* Обчислення площі перерізу мідної жили за стандартом AWG */
static double calculate_awg_area(awg_gauge_t gauge) {
    /* Діаметр за формулою AWG: d_n = 0.127 мм · 92^((36-n)/39) */
    double diameter_mm = 0.127 * pow(92.0, (36.0 - (double)gauge) / 39.0);
    double radius_mm = diameter_mm / 2.0;
    return 3.141592653589793 * radius_mm * radius_mm;
}

bool evaluate_harness_link(const harness_spec_t *spec, harness_result_t *res) {
    if (!spec || !res || spec->length_m <= 0.0 || spec->current_amps < 0.0) {
        return false;
    }

    res->wire_area_mm2 = calculate_awg_area(spec->gauge);
    double area_m2 = res->wire_area_mm2 * 1.0e-6;

    /* Розрахунок питомого опору з урахуванням температури: ρ(T) = ρ₂₀ · (1 + α · (T - 20)) */
    double delta_t = spec->operating_temp_c - 20.0;
    double rho_t = COPPER_RHO_20C * (1.0 + COPPER_TEMP_COEF * delta_t);

    /* Опір одного провідника: R = ρ · L / S */
    res->single_wire_res_ohm = rho_t * spec->length_m / area_m2;
    res->loop_res_ohm = 2.0 * res->single_wire_res_ohm;

    /* Падіння напруги та втрати */
    res->total_voltage_drop_v = spec->current_amps * res->loop_res_ohm;
    res->voltage_drop_percent = (spec->bus_voltage_v > 0.0)
        ? (res->total_voltage_drop_v / spec->bus_voltage_v) * 100.0
        : 0.0;

    /* Зміщення потенціалу землі на кінці лінії: ΔV_gnd = I_return · R_single */
    res->ground_shift_v = spec->current_amps * res->single_wire_res_ohm;
    res->thermal_loss_w = spec->current_amps * spec->current_amps * res->loop_res_ohm;

    /* Інженерні критерії: густина струму J ≤ 15 А/мм² для відкритого джгута */
    double current_density = spec->current_amps / res->wire_area_mm2;
    res->current_density_ok = (current_density <= 15.0);

    /* Запас завадостійкості: для 3.3V CMOS зсув землі понад 200 мВ неприпустимий */
    res->logic_margin_ok = (!spec->shared_ground) || (res->ground_shift_v < 0.200);

    return true;
}

void print_harness_report(const harness_spec_t *spec, const harness_result_t *res) {
    printf("=== ЗВІТ РОЗРАХУНКУ БОРТОВОЇ ЛІНІЇ (AWG %d, L=%.2f м, I=%.2f А) ===\n",
           spec->gauge, spec->length_m, spec->current_amps);
    printf("Переріз провідника:      %.4f мм²\n", res->wire_area_mm2);
    printf("Опір петлі (+ / -):      %.4f Ом\n", res->loop_res_ohm);
    printf("Падіння напруги на лінії: %.3f В (%.2f %% від %.1f В)\n",
           res->total_voltage_drop_v, res->voltage_drop_percent, spec->bus_voltage_v);
    printf("Зміщення потенціалу GND: %.3f В (%.1f мВ)\n",
           res->ground_shift_v, res->ground_shift_v * 1000.0);
    printf("Теплове розсіювання:     %.3f Вт\n", res->thermal_loss_w);
    printf("Статус густини струму:   %s\n", res->current_density_ok ? "НОРМА" : "ПЕРЕГРІВ (>15 А/мм²)");
    printf("Статус земляного зсуву:  %s\n", res->logic_margin_ok ? "БЕЗПЕЧНО" : "КРИТИЧНИЙ ЗСУВ ЗЕМЛІ!");
}
