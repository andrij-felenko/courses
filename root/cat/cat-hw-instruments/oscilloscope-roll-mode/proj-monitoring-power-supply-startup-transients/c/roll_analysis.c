#include "roll_analysis.h"
#include <math.h>

transient_result_t calculate_transient_duration(
    const roll_sample_t *samples,
    size_t sample_count,
    double steady_voltage_v,
    double tolerance_pct
) {
    transient_result_t result = {
        .is_valid = false,
        .transient_time_sec = 0.0,
        .steady_voltage_v = steady_voltage_v
    };

    if (samples == NULL || sample_count < 2 || tolerance_pct < 0.0) {
        return result;
    }

    double delta_v = fabs(steady_voltage_v * (tolerance_pct / 100.0));
    double v_min = steady_voltage_v - delta_v;
    double v_max = steady_voltage_v + delta_v;

    double t_start = samples[0].timestamp_sec;
    size_t last_out_index = 0;
    bool found_out_of_bounds = false;

    /* Пошук останньої вибірки, яка виходить за межі допускного коридору */
    for (size_t i = 0; i < sample_count; ++i) {
        if (samples[i].voltage_v < v_min || samples[i].voltage_v > v_max) {
            last_out_index = i;
            found_out_of_bounds = true;
        }
    }

    if (!found_out_of_bounds) {
        /* Сигнал із самого початку перебував у межах норми */
        result.is_valid = true;
        result.transient_time_sec = 0.0;
        return result;
    }

    /* Тривалість визначається як інтервал від початкової мітки t0 
     * до моменту останнього виходу за допускну зону */
    result.transient_time_sec = samples[last_out_index].timestamp_sec - t_start;
    result.is_valid = true;

    return result;
}

discharge_result_t estimate_battery_discharge_time(
    const roll_cursors_t *cursors,
    double cutoff_voltage_v
) {
    discharge_result_t result = {
        .is_valid = false,
        .discharge_rate_v_per_s = 0.0,
        .remaining_time_sec = 0.0
    };

    if (cursors == NULL) {
        return result;
    }

    double dt = cursors->t2.timestamp_sec - cursors->t1.timestamp_sec;
    double dv = cursors->t2.voltage_v - cursors->t1.voltage_v;

    /* Перевірка коректності часового інтервалу між курсорами */
    if (dt <= 0.0) {
        return result;
    }

    /* Швидкість розряду dV/dt (від'ємне значення при розряді) */
    double rate = dv / dt;
    result.discharge_rate_v_per_s = rate;

    /* Якщо напруга падає (dv < 0) і поточна напруга вища за напругу відсічки */
    if (rate < 0.0 && cursors->t2.voltage_v > cutoff_voltage_v) {
        double v_to_discharge = cursors->t2.voltage_v - cutoff_voltage_v;
        result.remaining_time_sec = v_to_discharge / fabs(rate);
        result.is_valid = true;
    } else if (cursors->t2.voltage_v <= cutoff_voltage_v) {
        /* Батарея вже розряджена нижче порогу */
        result.remaining_time_sec = 0.0;
        result.is_valid = true;
    }

    return result;
}
