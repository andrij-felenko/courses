#include "oscilloscope_trace.h"

#include <stdlib.h>
#include <math.h>

bool trace_init(oscilloscope_trace_t *trace, size_t initial_capacity) {
    if (!trace) {
        return false;
    }
    if (initial_capacity == 0) {
        initial_capacity = 64;
    }
    trace->samples = (sample_point_t *)malloc(initial_capacity * sizeof(sample_point_t));
    if (!trace->samples) {
        trace->count = 0;
        trace->capacity = 0;
        return false;
    }
    trace->count = 0;
    trace->capacity = initial_capacity;
    return true;
}

void trace_free(oscilloscope_trace_t *trace) {
    if (!trace) {
        return;
    }
    free(trace->samples);
    trace->samples = NULL;
    trace->count = 0;
    trace->capacity = 0;
}

void trace_clear(oscilloscope_trace_t *trace) {
    if (trace) {
        trace->count = 0;
    }
}

bool trace_add_sample(oscilloscope_trace_t *trace, double time_s, double voltage_v) {
    if (!trace) {
        return false;
    }
    if (trace->count >= trace->capacity) {
        size_t new_cap = (trace->capacity == 0) ? 64 : trace->capacity * 2;
        sample_point_t *new_samples = (sample_point_t *)realloc(trace->samples, new_cap * sizeof(sample_point_t));
        if (!new_samples) {
            return false;
        }
        trace->samples = new_samples;
        trace->capacity = new_cap;
    }
    trace->samples[trace->count].time_s = time_s;
    trace->samples[trace->count].voltage_v = voltage_v;
    trace->count++;
    return true;
}

bool trace_validate_monotonicity(const oscilloscope_trace_t *trace) {
    if (!trace || !trace->samples || trace->count < 2) {
        return trace != NULL;
    }
    for (size_t i = 1; i < trace->count; ++i) {
        /* Часова шкала повинна бути строго монотонно зростаючою */
        if (trace->samples[i].time_s <= trace->samples[i - 1].time_s) {
            return false;
        }
    }
    return true;
}

void trace_filter_outliers(oscilloscope_trace_t *trace, double max_spike_delta_v) {
    if (!trace || !trace->samples || trace->count < 3 || max_spike_delta_v <= 0.0) {
        return;
    }

    /*
     * Алгоритм виявлення поодиноких імпульсних викидів АЦП:
     * якщо поточна точка різко відхиляється від обох сусідів, замінюємо її
     * середнім значенням сусідів, зберігаючи круті ділянки монотонного фронту.
     */
    for (size_t i = 1; i < trace->count - 1; ++i) {
        const double v_prev = trace->samples[i - 1].voltage_v;
        const double v_curr = trace->samples[i].voltage_v;
        const double v_next = trace->samples[i + 1].voltage_v;

        const double delta_prev = fabs(v_curr - v_prev);
        const double delta_next = fabs(v_curr - v_next);
        const double neighbor_diff = fabs(v_prev - v_next);

        /* Викид: поточна точка далеко від обох сусідів, тоді як сусіди близькі між собою */
        if (delta_prev > max_spike_delta_v && delta_next > max_spike_delta_v && neighbor_diff < max_spike_delta_v) {
            trace->samples[i].voltage_v = 0.5 * (v_prev + v_next);
        }
    }
}

bool trace_calculate_amplitude_levels(const oscilloscope_trace_t *trace,
                                      double *out_baseline_v,
                                      double *out_steady_v) {
    if (!trace || !trace->samples || !out_baseline_v || !out_steady_v || trace->count < 10) {
        return false;
    }

    /* Визначаємо розмір вікна для квазістаціонарних ділянок (перші та останні 10% вибірок) */
    size_t window_size = trace->count / 10;
    if (window_size < 3) {
        window_size = 3;
    }
    if (window_size * 2 > trace->count) {
        return false;
    }

    /* Усереднення базової лінії (пре-імпульсний стаціонарний стан) */
    double baseline_sum = 0.0;
    for (size_t i = 0; i < window_size; ++i) {
        baseline_sum += trace->samples[i].voltage_v;
    }
    const double baseline_v = baseline_sum / (double)window_size;

    /* Усереднення стаціонарної полиці (пост-імпульсний усталений стан після перехідного процесу) */
    double steady_sum = 0.0;
    for (size_t i = trace->count - window_size; i < trace->count; ++i) {
        steady_sum += trace->samples[i].voltage_v;
    }
    const double steady_state_v = steady_sum / (double)window_size;

    /* Перевірка наявності змістовної амплітуди перепаду (понад 1 мВ) */
    if (fabs(steady_state_v - baseline_v) < 1.0e-3) {
        return false;
    }

    *out_baseline_v = baseline_v;
    *out_steady_v = steady_state_v;
    return true;
}

bool trace_find_threshold_crossing_time(const oscilloscope_trace_t *trace,
                                        double target_voltage,
                                        edge_slope_t slope,
                                        double *out_time_s) {
    if (!trace || !trace->samples || !out_time_s || trace->count < 2) {
        return false;
    }

    for (size_t i = 0; i < trace->count - 1; ++i) {
        const double v1 = trace->samples[i].voltage_v;
        const double v2 = trace->samples[i + 1].voltage_v;
        const double t1 = trace->samples[i].time_s;
        const double t2 = trace->samples[i + 1].time_s;

        if (slope == EDGE_SLOPE_RISING) {
            /* Шукаємо інтервал наростання, що містить порогове значення */
            if (v1 <= target_voltage && v2 >= target_voltage && v2 > v1) {
                /* Лінійна субдискретна інтерполяція моменту перетину порогу */
                const double fraction = (target_voltage - v1) / (v2 - v1);
                *out_time_s = t1 + fraction * (t2 - t1);
                return true;
            }
        } else {
            /* Шукаємо інтервал спаду, що містить порогове значення */
            if (v1 >= target_voltage && v2 <= target_voltage && v1 > v2) {
                const double fraction = (v1 - target_voltage) / (v1 - v2);
                *out_time_s = t1 + fraction * (t2 - t1);
                return true;
            }
        }
    }

    return false;
}

bool trace_calculate_rise_time(const oscilloscope_trace_t *trace,
                               double lower_fraction,
                               double upper_fraction,
                               double *out_rise_time_s) {
    if (!trace || !out_rise_time_s || lower_fraction >= upper_fraction ||
        lower_fraction < 0.0 || upper_fraction > 1.0) {
        return false;
    }

    double base_v = 0.0;
    double top_v = 0.0;
    if (!trace_calculate_amplitude_levels(trace, &base_v, &top_v)) {
        return false;
    }

    /* Перевіряємо, що сигнал дійсно є наростаючим */
    if (top_v <= base_v) {
        return false;
    }

    const double amplitude = top_v - base_v;
    const double v_lower = base_v + lower_fraction * amplitude;
    const double v_upper = base_v + upper_fraction * amplitude;

    double t_lower = 0.0;
    double t_upper = 0.0;

    const bool found_lower = trace_find_threshold_crossing_time(trace, v_lower, EDGE_SLOPE_RISING, &t_lower);
    const bool found_upper = trace_find_threshold_crossing_time(trace, v_upper, EDGE_SLOPE_RISING, &t_upper);

    if (found_lower && found_upper && t_upper > t_lower) {
        *out_rise_time_s = t_upper - t_lower;
        return true;
    }

    return false;
}
