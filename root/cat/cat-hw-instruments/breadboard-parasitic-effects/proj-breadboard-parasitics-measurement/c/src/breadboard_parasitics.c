#include "breadboard_parasitics.h"

#include <stdio.h>
#include <math.h>
#include <string.h>

/*
 * Математична константа ln(9) для розрахунку перехідного процесу 10%-90% у колі 1-го порядку:
 * v(t) = V_max * (1 - exp(-t/tau));
 * t_10 = -tau * ln(0.9);
 * t_90 = -tau * ln(0.1);
 * t_r = t_90 - t_10 = tau * ln(9) ≈ 2.197224577 * tau
 */
#define LN_9 2.1972245773362196
#define TWO_PI 6.2831853071795865

const char *contact_health_to_string(contact_health_t health) {
    switch (health) {
        case CONTACT_HEALTH_NEW:
            return "Новий (відмінний)";
        case CONTACT_HEALTH_ACCEPTABLE:
            return "Задовільний";
        case CONTACT_HEALTH_DEGRADED:
            return "Зношений / окислений";
        default:
            return "Невідомий";
    }
}

double calculate_total_capacitance(const test_bench_config_t *config, double rise_time_s) {
    if (!config || config->test_resistance_ohm <= 0.0 || rise_time_s <= 0.0) {
        return 0.0;
    }
    /* C_total = t_r / (ln(9) * R_test) */
    return rise_time_s / (LN_9 * config->test_resistance_ohm);
}

double calculate_parasitic_capacitance(const test_bench_config_t *config, double rise_time_s) {
    if (!config) {
        return 0.0;
    }
    const double c_total = calculate_total_capacitance(config, rise_time_s);
    /* Віднімаємо відому власну ємність вимірювального щупа (компенсація нуля вимірювального стенда) */
    const double c_parasitic = c_total - config->probe_capacitance_f;
    return (c_parasitic > 0.0) ? c_parasitic : 0.0;
}

double calculate_contact_resistance(const test_bench_config_t *config, double voltage_drop_v) {
    if (!config || voltage_drop_v <= 0.0 || config->test_load_current_a <= 0.0) {
        return 0.0;
    }
    /* R_cont = Delta_V / I_load */
    return voltage_drop_v / config->test_load_current_a;
}

double calculate_cutoff_frequency(const test_bench_config_t *config, double capacitance_f) {
    if (!config || capacitance_f <= 1.0e-15 || config->test_resistance_ohm <= 0.0) {
        return 0.0;
    }
    /* f_-3dB = 1 / (2 * pi * R * C) */
    return 1.0 / (TWO_PI * config->test_resistance_ohm * capacitance_f);
}

contact_health_t assess_contact_health(double contact_resistance_ohm) {
    /*
     * Критерії оцінки контактних затискачів безпаяльних макетних плат:
     * < 50 мОм: новий пружинний контакт із фосфористої бронзи
     * 50..200 мОм: прийнятний робочий контакт (допустиме поверхневе окиснення)
     * > 200 мОм: зношений, ослаблений або сильно окислений затискач
     */
    if (contact_resistance_ohm < 0.050) {
        return CONTACT_HEALTH_NEW;
    }
    if (contact_resistance_ohm <= 0.200) {
        return CONTACT_HEALTH_ACCEPTABLE;
    }
    return CONTACT_HEALTH_DEGRADED;
}

double extract_contact_voltage_drop(const oscilloscope_trace_t *load_trace) {
    if (!load_trace || !load_trace->samples || load_trace->count < 4) {
        return 0.0;
    }

    /*
     * Визначаємо напругу холостого ходу V_idle (початок осцилограми без струму)
     * та мінімальну стабільну напругу під час протікання імпульсу навантаження V_loaded
     */
    size_t init_count = load_trace->count / 10;
    if (init_count < 2) {
        init_count = 2;
    }

    double v_idle_sum = 0.0;
    for (size_t i = 0; i < init_count; ++i) {
        v_idle_sum += load_trace->samples[i].voltage_v;
    }
    const double v_idle = v_idle_sum / (double)init_count;

    double v_min = v_idle;
    for (size_t i = 0; i < load_trace->count; ++i) {
        if (load_trace->samples[i].voltage_v < v_min) {
            v_min = load_trace->samples[i].voltage_v;
        }
    }

    const double drop = v_idle - v_min;
    return (drop > 0.0) ? drop : 0.0;
}

bool analyze_breadboard_parasitics(const test_bench_config_t *config,
                                   const oscilloscope_trace_t *step_trace,
                                   double voltage_drop_v,
                                   parasitic_report_t *out_report) {
    if (!config || !step_trace || !out_report) {
        return false;
    }

    memset(out_report, 0, sizeof(parasitic_report_t));

    /* 1. Аналіз перехідного процесу наростання напруги */
    double rise_time_s = 0.0;
    trace_calculate_rise_time(step_trace, 0.10, 0.90, &rise_time_s);
    out_report->rise_time_ns = rise_time_s * 1.0e9;

    /* 2. Обчислення ємнісних параметрів */
    const double c_total_f = calculate_total_capacitance(config, rise_time_s);
    const double c_par_f = calculate_parasitic_capacitance(config, rise_time_s);
    out_report->total_capacitance_pf = c_total_f * 1.0e12;
    out_report->parasitic_capacitance_pf = c_par_f * 1.0e12;

    /* 3. Розрахунок граничної частоти зрізу RC-ланцюга */
    const double cutoff_hz = calculate_cutoff_frequency(config, c_par_f);
    out_report->cutoff_frequency_mhz = cutoff_hz / 1.0e6;

    /* 4. Обчислення контактного опору */
    out_report->voltage_drop_mv = voltage_drop_v * 1000.0;
    const double r_cont_ohm = calculate_contact_resistance(config, voltage_drop_v);
    out_report->contact_resistance_mohm = r_cont_ohm * 1000.0;
    out_report->health = assess_contact_health(r_cont_ohm);

    /* 5. Формування інженерних висновків та рекомендацій */
    const char *status_str = contact_health_to_string(out_report->health);
    const char *health_comment = "";
    if (out_report->health == CONTACT_HEALTH_NEW) {
        health_comment = "Низький опір (<50 мОм), придатний для живлення зі струмом до 1 А.";
    } else if (out_report->health == CONTACT_HEALTH_ACCEPTABLE) {
        health_comment = "Опір у межах норми. Рекомендовано обмежити тривалий струм до 0.5 А.";
    } else {
        health_comment = "УВАГА: контакт деградований (>200 мОм)! Ризик просідання VCC та нагріву.";
    }

    const char *cap_comment = (out_report->parasitic_capacitance_pf <= 3.0)
        ? "Паразитна ємність рейок у нормі (1-3 пФ). Придатний для I2C (до 400 кГц) та SPI (до 10 МГц)."
        : "Підвищена міжрейкова ємність. Можливі завали фронтів та ємнісні перехресні завади (crosstalk).";

    snprintf(out_report->notes, sizeof(out_report->notes),
             "Стан контактної групи: %s. %s %s",
             status_str, health_comment, cap_comment);

    return true;
}

bool analyze_breadboard_parasitics_traces(const test_bench_config_t *config,
                                          const oscilloscope_trace_t *step_trace,
                                          const oscilloscope_trace_t *load_trace,
                                          parasitic_report_t *out_report) {
    if (!load_trace) {
        return false;
    }
    const double drop_v = extract_contact_voltage_drop(load_trace);
    return analyze_breadboard_parasitics(config, step_trace, drop_v, out_report);
}
