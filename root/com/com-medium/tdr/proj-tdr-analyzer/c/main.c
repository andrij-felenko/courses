#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define C_SPEED 299792458.0  /* Швидкість світла у м/с */

typedef enum {
    FAULT_NONE = 0,
    FAULT_SHORT,
    FAULT_OPEN,
    FAULT_HIGH_IMPEDANCE,
    FAULT_LOW_IMPEDANCE,
    FAULT_CAPACITIVE_DIP,
    FAULT_INDUCTIVE_PEAK
} FaultType;

typedef struct {
    double distance_m;
    double time_ns;
    double gamma;
    double impedance_ohm;
    FaultType type;
} TdrEvent;

/*
 * Згладжування масиву сигналів ковзним середнім (вікно 2M+1)
 */
void filter_moving_average(const double* in_buf, double* out_buf, int len, int window_half) {
    for (int i = 0; i < len; ++i) {
        double sum = 0.0;
        int count = 0;
        for (int k = -window_half; k <= window_half; ++k) {
            int idx = i + k;
            if (idx >= 0 && idx < len) {
                sum += in_buf[idx];
                count++;
            }
        }
        out_buf[i] = sum / count;
    }
}

/*
 * Головна функція аналізу TDR-сигналу
 */
int analyze_tdr_trace(const double* raw_voltage, int num_samples, double dt_sec,
                      double z0_ohm, double er_relative,
                      double* out_distance, double* out_impedance,
                      TdrEvent* out_events, int max_events, int* out_event_count) {
    if (!raw_voltage || num_samples < 20 || dt_sec <= 0.0 || z0_ohm <= 0.0 || er_relative < 1.0) {
        return -1;
    }

    /* Фільтрація шуму */
    double* smooth_v = (double*)malloc(num_samples * sizeof(double));
    if (!smooth_v) return -2;
    filter_moving_average(raw_voltage, smooth_v, num_samples, 2);

    /* 1. Обчислення базової лінії V_base (перші 10 відліків) */
    double v_base = 0.0;
    for (int i = 0; i < 10; ++i) {
        v_base += smooth_v[i];
    }
    v_base /= 10.0;

    /* 2. Пошук амплітуди падаючого перепаду V_inc */
    double v_max = smooth_v[0];
    for (int i = 1; i < num_samples; ++i) {
        if (smooth_v[i] > v_max) v_max = smooth_v[i];
    }
    double v_inc = v_max - v_base;
    if (v_inc < 1e-4) {
        free(smooth_v);
        return -3; /* Перепад не виявлено */
    }

    /* 3. Детектування точки фронту t0 (перетин 50% V_inc із субдискретною інтерполяцією) */
    double v_thresh = v_base + 0.5 * v_inc;
    double t0_sample_idx = -1.0;

    for (int i = 0; i < num_samples - 1; ++i) {
        if (smooth_v[i] <= v_thresh && smooth_v[i+1] > v_thresh) {
            double dy = smooth_v[i+1] - smooth_v[i];
            double fraction = (dy > 1e-9) ? ((v_thresh - smooth_v[i]) / dy) : 0.0;
            t0_sample_idx = i + fraction;
            break;
        }
    }

    if (t0_sample_idx < 0.0) {
        free(smooth_v);
        return -4;
    }

    /* 4. Швидкість поширення хвилі */
    double v_prop = C_SPEED / sqrt(er_relative);

    /* 5. Розрахунок профілю відстані та імпедансу */
    for (int i = 0; i < num_samples; ++i) {
        double dt = (i - t0_sample_idx) * dt_sec;
        out_distance[i] = (dt > 0.0) ? (v_prop * dt / 2.0) : 0.0;

        double gamma = (smooth_v[i] - (v_base + v_inc)) / v_inc;
        if (gamma > 0.999) gamma = 0.999;
        if (gamma < -0.999) gamma = -0.999;

        out_impedance[i] = z0_ohm * (1.0 + gamma) / (1.0 - gamma);
    }

    /* 6. Пошук неоднорідностей (Event Detection) */
    int event_cnt = 0;
    int start_search = (int)t0_sample_idx + 5;

    for (int i = start_search; i < num_samples - 1; ++i) {
        double gamma = (smooth_v[i] - (v_base + v_inc)) / v_inc;

        /* Перевірка на суттєве відхилення (пороги) */
        if (fabs(gamma) > 0.12) {
            /* Пошук локального екстремуму */
            if ((smooth_v[i] >= smooth_v[i-1] && smooth_v[i] >= smooth_v[i+1]) ||
                (smooth_v[i] <= smooth_v[i-1] && smooth_v[i] <= smooth_v[i+1])) {

                if (event_cnt < max_events) {
                    out_events[event_cnt].distance_m = out_distance[i];
                    out_events[event_cnt].time_ns = (i - t0_sample_idx) * dt_sec * 1e9;
                    out_events[event_cnt].gamma = gamma;
                    out_events[event_cnt].impedance_ohm = out_impedance[i];

                    if (gamma > 0.85) out_events[event_cnt].type = FAULT_OPEN;
                    else if (gamma < -0.85) out_events[event_cnt].type = FAULT_SHORT;
                    else if (gamma > 0.15) out_events[event_cnt].type = FAULT_HIGH_IMPEDANCE;
                    else if (gamma < -0.15) out_events[event_cnt].type = FAULT_LOW_IMPEDANCE;
                    else out_events[event_cnt].type = FAULT_NONE;

                    event_cnt++;
                    i += 3; /* Пропуск сусідніх відліків для виключення дублювання */
                }
            }
        }
    }

    if (out_event_count) *out_event_count = event_cnt;
    free(smooth_v);
    return 0;
}
