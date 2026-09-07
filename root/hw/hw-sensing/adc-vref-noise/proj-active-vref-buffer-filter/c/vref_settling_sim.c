#include "vref_settling_sim.h"
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

double vref_calculate_phase_margin(const vref_buffer_config_t *buf)
{
    if (buf == NULL || buf->gbw_hz <= 0.0 || buf->c_filt_f <= 0.0) {
        return 0.0;
    }

    /* Полюс навантаження, утворений вихідним опором ОП та ємністю фільтра */
    double f_pole = 1.0 / (2.0 * M_PI * (buf->r_out_open_loop + buf->r_iso_ohm) * buf->c_filt_f);

    /* Нуль компенсації, утворений ізолюючим резистором та конденсатором фільтра */
    double f_zero = 1.0 / (2.0 * M_PI * buf->r_iso_ohm * buf->c_filt_f);

    /* Частота одиничного підсилення петлі з урахуванням ємнісного навантаження */
    double f_unity = sqrt(buf->gbw_hz * f_pole);

    /* Розрахунок фазового зсуву на частоті перетину одиничного підсилення */
    double phase_lag_rad = atan(f_unity / f_pole) - atan(f_unity / f_zero);
    double phase_margin_rad = M_PI / 2.0 - phase_lag_rad;

    double phase_margin_deg = phase_margin_rad * (180.0 / M_PI);

    /* Нормалізація в межах 0..90 градусів */
    if (phase_margin_deg < 0.0) {
        phase_margin_deg = 0.0;
    } else if (phase_margin_deg > 90.0) {
        phase_margin_deg = 90.0;
    }

    return phase_margin_deg;
}

bool vref_simulate_cdac_settling(
    const vref_buffer_config_t *buf,
    const cdac_switch_event_t *cdac,
    double dt_s,
    vref_sim_result_t *result)
{
    if (buf == NULL || cdac == NULL || result == NULL || dt_s <= 0.0) {
        return false;
    }
    if (cdac->resolution_bits == 0 || cdac->t_settle_budget_s <= 0.0) {
        return false;
    }

    /* Розрахунок ціни молодшого розряду (LSB) */
    double total_codes = pow(2.0, (double)cdac->resolution_bits);
    double lsb_v = buf->vref_nominal_v / total_codes;

    /* Миттєвий перерозподіл заряду на початку такту комутації (t = 0+) */
    double c_total = buf->c_filt_f + cdac->c_sample_f;
    double delta_q = cdac->c_sample_f * cdac->v_step_v;
    double initial_drop_v = delta_q / c_total;

    /* Початковий стан напруги на виводі VREF */
    double v_cap = buf->vref_nominal_v - initial_drop_v;
    double max_drop = initial_drop_v;

    /* Еквівалентний замкнений вихідний опір буфера на низьких частотах */
    double r_closed_loop = buf->r_out_open_loop / 1000.0; /* Приблизне придушення петлею */
    if (r_closed_loop < 0.01) {
        r_closed_loop = 0.01;
    }

    /* Постійна часу відновлення заряду буфером */
    double tau_recovery_s = (r_closed_loop + buf->r_iso_ohm + buf->esr_c_filt_ohm) * buf->c_filt_f;
    if (tau_recovery_s < 1.0 / (2.0 * M_PI * buf->gbw_hz)) {
        tau_recovery_s = 1.0 / (2.0 * M_PI * buf->gbw_hz);
    }

    /* Дискретне інтегрування за методом Ейлера */
    double current_time_s = 0.0;
    while (current_time_s < cdac->t_settle_budget_s) {
        double dv = (buf->vref_nominal_v - v_cap) / tau_recovery_s;
        v_cap += dv * dt_s;
        current_time_s += dt_s;
    }

    /* Залишкова похибка напруги в кінці часового вікна */
    double residual_v = fabs(buf->vref_nominal_v - v_cap);
    double error_in_lsb = residual_v / lsb_v;

    result->max_voltage_drop_v = max_drop;
    result->residual_error_v = residual_v;
    result->error_lsb = error_in_lsb;
    result->phase_margin_deg = vref_calculate_phase_margin(buf);
    result->is_settled_within_half_lsb = (error_in_lsb <= 0.5);

    return true;
}
