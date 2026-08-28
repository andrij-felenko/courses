#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define M_PI_F 3.14159265358979323846f

typedef struct {
    float real;
    float imag;
} ComplexVec;

typedef struct {
    float mass_mg;
    float angle_deg;
    float residual_amp;
} BalanceResult;

static inline ComplexVec complex_make(float r, float i) {
    ComplexVec v = { .real = r, .imag = i };
    return v;
}

static inline ComplexVec complex_sub(ComplexVec a, ComplexVec b) {
    return complex_make(a.real - b.real, a.imag - b.imag);
}

static inline ComplexVec complex_div(ComplexVec a, ComplexVec b) {
    float denom = b.real * b.real + b.imag * b.imag;
    if (denom < 1e-12f) return complex_make(0.0f, 0.0f);
    return complex_make((a.real * b.real + a.imag * b.imag) / denom,
                        (a.imag * b.real - a.real * b.imag) / denom);
}

static inline float complex_mag(ComplexVec v) {
    return sqrtf(v.real * v.real + v.imag * v.imag);
}

static inline float complex_arg_deg(ComplexVec v) {
    float deg = atan2f(v.imag, v.real) * (180.0f / M_PI_F);
    if (deg < 0.0f) deg += 360.0f;
    return deg;
}

// Виділення амплітуди й фази гармоніки 1x RPM синхронним фазовим детектором
ComplexVec extract_1x_vector(const float *samples, size_t num_samples, 
                             float sample_rate, float rpm_freq) {
    float sum_cos = 0.0f;
    float sum_sin = 0.0f;
    float dt = 1.0f / sample_rate;
    float omega = 2.0f * M_PI_F * rpm_freq;

    for (size_t i = 0; i < num_samples; i++) {
        float t = (float)i * dt;
        float phase = omega * t;
        // Вікно Ганна для усунення крайових стрибків
        float w = 0.5f * (1.0f - cosf(2.0f * M_PI_F * (float)i / (float)(num_samples - 1)));
        float val = samples[i] * w;

        sum_cos += val * cosf(phase);
        sum_sin += val * sinf(phase);
    }

    // Нормалізація амплітуди з урахуванням втрат вікна Ганна (множник 4/N)
    float scale = 4.0f / (float)num_samples;
    return complex_make(sum_cos * scale, sum_sin * scale);
}

// Розрахунок параметрів коригувального вантажу
BalanceResult calculate_correction(ComplexVec v0, ComplexVec v1, 
                                   float trial_mass_mg, float trial_angle_deg) {
    BalanceResult res;
    ComplexVec delta_v = complex_sub(v1, v0);
    float delta_mag = complex_mag(delta_v);

    if (delta_mag < 1e-6f) {
        // Пробний вантаж не спричинив змін — недостатня маса або механічне заклинювання
        res.mass_mg = 0.0f;
        res.angle_deg = 0.0f;
        res.residual_amp = complex_mag(v0);
        return res;
    }

    // Вектор дисбалансу пробного вантажу
    float rad_t = trial_angle_deg * (M_PI_F / 180.0f);
    ComplexVec ut = complex_make(trial_mass_mg * cosf(rad_t), trial_mass_mg * sinf(rad_t));

    // Коефіцієнт впливу S = delta_V / Ut
    ComplexVec sens = complex_div(delta_v, ut);

    // Коригувальний дисбаланс Uc = -V0 / S
    ComplexVec neg_v0 = complex_make(-v0.real, -v0.imag);
    ComplexVec uc = complex_div(neg_v0, sens);

    res.mass_mg = complex_mag(uc);
    res.angle_deg = complex_arg_deg(uc);
    res.residual_amp = 0.0f; // Теоретичний ідеальний залишок

    return res;
}

int main(void) {
    const float fs = 8000.0f;      // Частота дискретизації АЦП: 8 кГц
    const float f_rpm = 200.0f;    // 12000 RPM = 200 Гц
    const size_t n = 2048;         // Розмір вибірки аналізу
    float samples_run0[2048];
    float samples_run1[2048];

    // Моделювання сирого сигналу для базового пуску: V0 = 12.0 м/с² під 40°
    for (size_t i = 0; i < n; i++) {
        float t = (float)i / fs;
        float p0 = 2.0f * M_PI_F * f_rpm * t + 40.0f * (M_PI_F / 180.0f);
        samples_run0[i] = 12.0f * cosf(p0) + 1.2f * sinf(2.0f * M_PI_F * 600.0f * t);
    }

    // Моделювання для пуску з пробним вантажем 100 мг на 0°: V1 = 6.5 м/с² під 110°
    for (size_t i = 0; i < n; i++) {
        float t = (float)i / fs;
        float p1 = 2.0f * M_PI_F * f_rpm * t + 110.0f * (M_PI_F / 180.0f);
        samples_run1[i] = 6.5f * cosf(p1) + 1.1f * sinf(2.0f * M_PI_F * 600.0f * t);
    }

    ComplexVec v0 = extract_1x_vector(samples_run0, n, fs, f_rpm);
    ComplexVec v1 = extract_1x_vector(samples_run1, n, fs, f_rpm);

    printf("Базовий вектор V0:    |V0| = %6.2f m/s^2, phi = %5.1f deg\n",
           complex_mag(v0), complex_arg_deg(v0));
    printf("Вектор з вантажем V1: |V1| = %6.2f m/s^2, phi = %5.1f deg\n",
           complex_mag(v1), complex_arg_deg(v1));

    BalanceResult sol = calculate_correction(v0, v1, 100.0f, 0.0f);

    printf("\n=== РЕЗУЛЬТАТ ДИНАМІЧНОГО БАЛАНСУВАННЯ ===\n");
    printf("1. Зніміть пробний вантаж (100.0 мг на 0.0 deg).\n");
    printf("2. Встановіть балансувальний вантаж:\n");
    printf("   -> Маса тягарця:  %6.1f мг\n", sol.mass_mg);
    printf("   -> Кут установки: %6.1f градусів від мітки\n", sol.angle_deg);

    return 0;
}
