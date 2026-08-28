#include <stdio.h>
#include <math.h>
#include <stdbool.h>

#define KB_EV 8.617333262e-5 /* Стала Больцмана в еВ/К */
#define T_REF_K (85.0 + 273.15) /* Опорна температура +85 °C у Кельвінах */

typedef enum {
    CAP_TYPE_NBO,      /* Оксидно-ніобієвий конденсатор (NbO) */
    CAP_TYPE_TA_MNO2   /* Класичний танталовий конденсатор (Ta-MnO2) */
} CapType;

typedef struct {
    CapType type;
    const char *part_number;
    double capacitance_uf;   /* Ємність у мікрофарадах */
    double rated_voltage_v;  /* Номінальна напруга V_rated */
    double esr_ohm;          /* Послідовний опір ESR на 100 кГц */
    double r_th_c_per_w;     /* Тепловий опір корпусу, °C/Вт */
    double base_fit;         /* Базовий FIT за номінальних умов (+85 °C, V_rated) */
} CapacitorSpec;

typedef struct {
    double bus_voltage_v;    /* Робоча напруга шини живлення */
    double ripple_current_a; /* Діючий струм пульсацій I_rms */
    double source_res_ohm;   /* Опір джерела та проводки плати */
    double loop_inductance_nh;/* Паразитна індуктивність контуру в нГн */
    double operating_temp_c; /* Робоча температура навколишнього середовища в °C */
} CircuitCondition;

typedef struct {
    double inrush_peak_current_a;
    double didt_max_a_per_us;
    double damping_factor;
    double power_loss_w;
    double temp_rise_c;
    double allowed_voltage_v;
    bool is_derating_valid;
    bool is_thermal_valid;
    double operating_fit;
    double mtbf_years;
    const char *safety_status;
} AnalysisResult;

bool evaluate_capacitor(const CapacitorSpec *cap, const CircuitCondition *cond, AnalysisResult *out) {
    if (!cap || !cond || !out) return false;

    /* 1. Розрахунок параметрів пускового струму та коливального контуру */
    double total_r = cond->source_res_ohm + cap->esr_ohm;
    if (total_r < 1e-4) total_r = 1e-4;
    out->inrush_peak_current_a = cond->bus_voltage_v / total_r;

    double loop_l_h = cond->loop_inductance_nh * 1e-9;
    double cap_f = cap->capacitance_uf * 1e-6;

    if (loop_l_h > 1e-12) {
        out->didt_max_a_per_us = (cond->bus_voltage_v / loop_l_h) * 1e-6;
        out->damping_factor = (total_r / 2.0) * sqrt(cap_f / loop_l_h);
    } else {
        out->didt_max_a_per_us = 0.0;
        out->damping_factor = 10.0; /* Аперіодичний */
    }

    /* 2. Розрахунок втрат потужності та власного нагріву */
    out->power_loss_w = (cond->ripple_current_a * cond->ripple_current_a) * cap->esr_ohm;
    out->temp_rise_c = out->power_loss_w * cap->r_th_c_per_w;
    out->is_thermal_valid = (out->temp_rise_c <= 10.0);

    /* 3. Перевірка температурного дератингу напруги */
    double t_effective = cond->operating_temp_c + out->temp_rise_c;

    if (cap->type == CAP_TYPE_NBO) {
        if (t_effective <= 85.0) {
            out->allowed_voltage_v = cap->rated_voltage_v * 0.80;
        } else if (t_effective <= 125.0) {
            double derate_factor = 0.80 - 0.30 * ((t_effective - 85.0) / 40.0);
            out->allowed_voltage_v = cap->rated_voltage_v * derate_factor;
        } else {
            out->allowed_voltage_v = 0.0;
        }
    } else { /* Ta-MnO2 */
        if (t_effective <= 85.0) {
            out->allowed_voltage_v = cap->rated_voltage_v * 0.50;
        } else if (t_effective <= 125.0) {
            double derate_factor = 0.50 - 0.17 * ((t_effective - 85.0) / 40.0);
            out->allowed_voltage_v = cap->rated_voltage_v * derate_factor;
        } else {
            out->allowed_voltage_v = 0.0;
        }
    }

    out->is_derating_valid = (cond->bus_voltage_v <= out->allowed_voltage_v);

    /* 4. Оцінка надійності: FIT та MTBF */
    double voltage_ratio = cond->bus_voltage_v / cap->rated_voltage_v;
    if (voltage_ratio > 1.2) voltage_ratio = 1.2;

    double n_exp = (cap->type == CAP_TYPE_NBO) ? 3.5 : 14.0;
    double af_v = pow(voltage_ratio, n_exp);

    double t_op_k = t_effective + 273.15;
    double ea_ev = 0.15;
    double delta_inv_t = (1.0 / T_REF_K) - (1.0 / t_op_k);
    double af_t = exp((ea_ev / KB_EV) * delta_inv_t);

    out->operating_fit = cap->base_fit * af_v * af_t;
    if (out->operating_fit > 0.0) {
        out->mtbf_years = (1.0e9 / out->operating_fit) / 8760.0;
    } else {
        out->mtbf_years = 0.0;
    }

    /* Формування вердикту безпеки */
    if (!out->is_derating_valid) {
        out->safety_status = (cap->type == CAP_TYPE_NBO) 
            ? "ПОПЕРЕДЖЕННЯ: перевищено дератинг (відмова безпечна: перехід у розрив)"
            : "КРИТИЧНА ПОМИЛКА: порушено дератинг 50%! Ризик займання танталу!";
    } else if (!out->is_thermal_valid) {
        out->safety_status = "УВАГА: надмірний перегрів від пульсацій струму (dT > 10 °C)";
    } else {
        out->safety_status = "НОРМА: дератинг, пульсації та надійність у межах стандарту";
    }

    return true;
}

int main(void) {
    CapacitorSpec nbo_cap = {
        .type = CAP_TYPE_NBO,
        .part_number = "NOJB107M006R0200 (AVX 100uF / 6.3V)",
        .capacitance_uf = 100.0,
        .rated_voltage_v = 6.3,
        .esr_ohm = 0.200,
        .r_th_c_per_w = 110.0,
        .base_fit = 5000.0
    };

    CapacitorSpec ta_cap = {
        .type = CAP_TYPE_TA_MNO2,
        .part_number = "TAJB107M006RNJ (KEMET 100uF / 6.3V)",
        .capacitance_uf = 100.0,
        .rated_voltage_v = 6.3,
        .esr_ohm = 0.250,
        .r_th_c_per_w = 110.0,
        .base_fit = 5000.0
    };

    CircuitCondition bus_5v = {
        .bus_voltage_v = 5.0,
        .ripple_current_a = 0.450, /* 450 мА RMS */
        .source_res_ohm = 0.030,
        .loop_inductance_nh = 15.0,
        .operating_temp_c = 65.0
    };

    AnalysisResult res_nbo, res_ta;
    evaluate_capacitor(&nbo_cap, &bus_5v, &res_nbo);
    evaluate_capacitor(&ta_cap, &bus_5v, &res_ta);

    printf("=================================================================\n");
    printf("РОЗРАХУНОК НАДІЙНОСТІ ТА ДЕРАТИНГУ НА ШИНІ 5.0 В (T = +65 °C)\n");
    printf("=================================================================\n");

    printf("\n1. ОКСИД НІОБІЮ: %s\n", nbo_cap.part_number);
    printf("   Пусковий струм: %.1f А, dI/dt: %.1f А/мкс, Демпфування zeta: %.2f\n", 
           res_nbo.inrush_peak_current_a, res_nbo.didt_max_a_per_us, res_nbo.damping_factor);
    printf("   Перегрів від пульсацій: +%.1f °C (Втрати: %.3f Вт)\n", res_nbo.temp_rise_c, res_nbo.power_loss_w);
    printf("   Дозволена напруга: %.2f В (Факт: %.2f В) -> %s\n", 
           res_nbo.allowed_voltage_v, bus_5v.bus_voltage_v, res_nbo.is_derating_valid ? "ПРОХОДИТЬ" : "НЕ ПРОХОДИТЬ");
    printf("   Інтенсивність відмов: %.1f FIT | MTBF: %.1f років\n", res_nbo.operating_fit, res_nbo.mtbf_years);
    printf("   Статус: %s\n", res_nbo.safety_status);

    printf("\n2. ТАНТАЛ MnO2: %s\n", ta_cap.part_number);
    printf("   Пусковий струм: %.1f А, dI/dt: %.1f А/мкс, Демпфування zeta: %.2f\n", 
           res_ta.inrush_peak_current_a, res_ta.didt_max_a_per_us, res_ta.damping_factor);
    printf("   Перегрів від пульсацій: +%.1f °C (Втрати: %.3f Вт)\n", res_ta.temp_rise_c, res_ta.power_loss_w);
    printf("   Дозволена напруга: %.2f В (Факт: %.2f В) -> %s\n", 
           res_ta.allowed_voltage_v, bus_5v.bus_voltage_v, res_ta.is_derating_valid ? "ПРОХОДИТЬ" : "НЕ ПРОХОДИТЬ");
    printf("   Інтенсивність відмов: %.1f FIT | MTBF: %.1f років\n", res_ta.operating_fit, res_ta.mtbf_years);
    printf("   Статус: %s\n", res_ta.safety_status);

    return 0;
}
