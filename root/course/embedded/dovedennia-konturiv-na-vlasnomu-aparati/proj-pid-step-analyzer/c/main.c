#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define MAX_SAMPLES 1024

typedef struct {
    double setpoint;          // Амплітуда виявленої сходинки, deg/s
    double latency_ms;        // Час запізнення реакції (вихід на 5%), мс
    double rise_time_ms;      // Час наростання від 10% до 90%, мс
    double overshoot_pct;     // Величина перерегулювання, %
    double settling_time_ms;  // Час заспокоєння до коридору 5%, мс
    double d_noise_rms;       // Середньоквадратичний шум D-терма на плато
    int    oscillation_count; // Кількість перетинів коридору (дзвін)
    bool   is_valid_step;     // Ознака валідної та придатної до аналізу сходинки
} StepMetrics;

typedef enum {
    TUNE_PERFECT = 0,
    TUNE_P_TOO_LOW,
    TUNE_P_TOO_HIGH,
    TUNE_D_TOO_LOW,
    TUNE_D_TOO_HIGH_NOISE,
    TUNE_SYSTEM_LAGGY
} TuneDiagnostic;

// Перевірка спокою системи перед початком сходинки
static bool verify_pre_step_quiescence(const double *target, const double *actual, int start_idx) {
    if (start_idx < 10) return true;
    for (int i = start_idx - 10; i < start_idx; ++i) {
        if (fabs(target[i] - actual[i]) > 25.0) {
            return false;
        }
    }
    return true;
}

// Аналіз масиву відліків сходинки перехідного процесу
static StepMetrics analyze_step_response(const uint64_t *time_us,
                                        const double *target,
                                        const double *actual,
                                        const double *d_term,
                                        int n) {
    StepMetrics m = {0};
    if (n < 25 || n > MAX_SAMPLES) return m;

    double t0 = target[0];
    double t_final = target[n - 1];
    double step_amp = t_final - t0;

    // Сходинка має бути чіткою та енергійною (> 35 deg/s)
    if (fabs(step_amp) < 35.0) return m;
    if (!verify_pre_step_quiescence(target, actual, 5)) return m;

    m.setpoint = step_amp;
    m.is_valid_step = true;

    uint64_t t_start = time_us[0];
    uint64_t t_5pct = 0, t_10pct = 0, t_90pct = 0;
    double max_val = actual[0];
    int peak_idx = 0;

    double target_5  = t0 + 0.05 * step_amp;
    double target_10 = t0 + 0.10 * step_amp;
    double target_90 = t0 + 0.90 * step_amp;
    double band_low  = t_final - 0.05 * fabs(step_amp);
    double band_high = t_final + 0.05 * fabs(step_amp);

    for (int i = 1; i < n; ++i) {
        double val = actual[i];

        // Фіксація часу запізнення реакції (вихід на 5%)
        if (!t_5pct && ((step_amp > 0 && val >= target_5) || (step_amp < 0 && val <= target_5))) {
            t_5pct = time_us[i];
        }
        // Фіксація часових позначок наростання (10% та 90%)
        if (!t_10pct && ((step_amp > 0 && val >= target_10) || (step_amp < 0 && val <= target_10))) {
            t_10pct = time_us[i];
        }
        if (!t_90pct && ((step_amp > 0 && val >= target_90) || (step_amp < 0 && val <= target_90))) {
            t_90pct = time_us[i];
        }

        // Пошук абсолютного піка для визначення перерегулювання
        if (step_amp > 0) {
            if (val > max_val) { max_val = val; peak_idx = i; }
        } else {
            if (val < max_val) { max_val = val; peak_idx = i; }
        }
    }

    if (t_5pct > t_start) {
        m.latency_ms = (double)(t_5pct - t_start) / 1000.0;
    }
    if (t_90pct > t_10pct && t_10pct > 0) {
        m.rise_time_ms = (double)(t_90pct - t_10pct) / 1000.0;
    }

    // Обчислення відсотка перерегулювання
    if (step_amp > 0 && max_val > t_final) {
        m.overshoot_pct = ((max_val - t_final) / step_amp) * 100.0;
    } else if (step_amp < 0 && max_val < t_final) {
        m.overshoot_pct = ((t_final - max_val) / fabs(step_amp)) * 100.0;
    } else {
        m.overshoot_pct = 0.0;
    }

    // Час встановлення та підрахунок перетинів межі коридору 5%
    uint64_t t_settle = 0;
    int crossings = 0;
    for (int i = peak_idx; i < n; ++i) {
        if (actual[i] < band_low || actual[i] > band_high) {
            t_settle = time_us[i];
            crossings++;
        }
    }
    m.settling_time_ms = (t_settle > t_start) ? (double)(t_settle - t_start) / 1000.0 : m.rise_time_ms;
    m.oscillation_count = crossings;

    // Оцінка високочастотного шуму D-терма на плато сходинки
    double sum_sq = 0.0;
    int noise_samples = 0;
    int start_noise = n / 2;
    for (int i = start_noise + 1; i < n; ++i) {
        double delta = d_term[i] - d_term[i - 1];
        sum_sq += delta * delta;
        noise_samples++;
    }
    m.d_noise_rms = (noise_samples > 0) ? sqrt(sum_sq / noise_samples) : 0.0;

    return m;
}

// Генерація діагностичного висновку за виміряними метриками
static TuneDiagnostic evaluate_tuning(const StepMetrics *m) {
    if (!m->is_valid_step) return TUNE_PERFECT;

    if (m->latency_ms > 24.0) {
        return TUNE_SYSTEM_LAGGY; // Завеликий лаг фільтрів або слабка тяга
    }
    if (m->d_noise_rms > 35.0) {
        return TUNE_D_TOO_HIGH_NOISE; // Небезпека високочастотного перегріву моторів
    }
    if (m->overshoot_pct > 20.0 && m->rise_time_ms < 32.0) {
        return (m->oscillation_count > 4) ? TUNE_P_TOO_HIGH : TUNE_D_TOO_LOW;
    }
    if (m->rise_time_ms > 90.0 && m->overshoot_pct < 2.0) {
        return TUNE_P_TOO_LOW; // Млява реакція, брак пропорційного підсилення
    }
    return TUNE_PERFECT;
}
