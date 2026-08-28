#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <stddef.h>

/* Результати вимірювання параметрів імпульсного сигналу */
typedef struct {
    double frequency_hz;   /* Частота сигналу f = 1 / T */
    double period_s;       /* Період сигналу T */
    double pulse_width_s;  /* Тривалість імпульсу th */
    double duty_cycle;     /* Коефіцієнт заповнення D (0.0 .. 1.0) */
    double duty_factor;    /* Шпаруватість S = 1 / D */
    bool is_valid;         /* Ознака валідності розрахунку */
} PulseMetrics;

/* Стан кінцевого автомата подвійного захоплення таймера */
typedef struct {
    uint32_t timer_clock_hz; /* Тактова частота лічильника таймера */
    uint32_t last_rise_tick; /* Відлік лічильника останнього наростання */
    uint32_t last_fall_tick; /* Відлік лічильника останнього спаду */
    bool has_prev_rise;      /* Зафіксовано попередній передній фронт */
    bool has_fall;           /* Зафіксовано задній фронт у поточному циклі */
} TimerCaptureFSM;

/* Ініціалізація автомата захоплення */
void pulse_fsm_init(TimerCaptureFSM *fsm, uint32_t timer_clock_hz) {
    if (!fsm) return;
    fsm->timer_clock_hz = timer_clock_hz;
    fsm->last_rise_tick = 0;
    fsm->last_fall_tick = 0;
    fsm->has_prev_rise = false;
    fsm->has_fall = false;
}

/* Обробник події переднього фронту (Rising Edge Interrupt) */
bool pulse_fsm_on_rising(TimerCaptureFSM *fsm, uint32_t tick, PulseMetrics *out_metrics) {
    if (!fsm || !out_metrics) return false;
    out_metrics->is_valid = false;

    if (fsm->has_prev_rise && fsm->has_fall) {
        /* Беззнакове віднімання автоматично враховує циклічне переповнення */
        uint32_t period_ticks = tick - fsm->last_rise_tick;
        uint32_t high_ticks   = fsm->last_fall_tick - fsm->last_rise_tick;

        if (period_ticks > 0 && high_ticks <= period_ticks && fsm->timer_clock_hz > 0) {
            double clk = (double)fsm->timer_clock_hz;
            out_metrics->period_s = (double)period_ticks / clk;
            out_metrics->pulse_width_s = (double)high_ticks / clk;
            out_metrics->frequency_hz = clk / (double)period_ticks;
            out_metrics->duty_cycle = (double)high_ticks / (double)period_ticks;
            out_metrics->duty_factor = (high_ticks > 0) ? (1.0 / out_metrics->duty_cycle) : 0.0;
            out_metrics->is_valid = true;
        }
    }

    fsm->last_rise_tick = tick;
    fsm->has_prev_rise = true;
    fsm->has_fall = false; /* Очікуємо спад у новому періоді */
    return out_metrics->is_valid;
}

/* Обробник події заднього фронту (Falling Edge Interrupt) */
void pulse_fsm_on_falling(TimerCaptureFSM *fsm, uint32_t tick) {
    if (!fsm) return;
    if (fsm->has_prev_rise) {
        fsm->last_fall_tick = tick;
        fsm->has_fall = true;
    }
}

/* Розрахунок True RMS та інтегральних норм для масиву вибірок АЦП */
void calculate_discrete_rms(const float *samples, size_t count,
                            float *out_dc, float *out_rms,
                            float *out_crest, float *out_form) {
    if (!samples || count == 0 || !out_dc || !out_rms || !out_crest || !out_form) return;

    double sum = 0.0;
    double sum_sq = 0.0;
    double sum_abs = 0.0;
    float peak = 0.0f;

    for (size_t i = 0; i < count; ++i) {
        float val = samples[i];
        sum += val;
        sum_sq += (double)val * (double)val;
        float abs_val = fabsf(val);
        sum_abs += (double)abs_val;
        if (abs_val > peak) {
            peak = abs_val;
        }
    }

    double mean = sum / (double)count;
    double mean_sq = sum_sq / (double)count;
    double rms = sqrt(mean_sq);
    double rectified_avg = sum_abs / (double)count;

    *out_dc = (float)mean;
    *out_rms = (float)rms;
    *out_crest = (rms > 1e-9) ? (peak / (float)rms) : 0.0f;
    *out_form  = (rectified_avg > 1e-9) ? ((float)rms / (float)rectified_avg) : 0.0f;
}
