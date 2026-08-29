#include "pio.h"

#include <math.h>

#define PIO_PI     3.14159265358979f
#define TREND_TC   0.8f  /* стала часу видалення тренду, с */
#define AMP_TC     0.7f  /* витік огинаючої, с */
#define WINDOW_SEC 1.5f  /* вікно оцінки частоти, с */

void pio_init(PioMonitor *m, float dt) {
    m->dt = dt;
    m->trend = 0.0f;
    m->hp = 0.0f;
    m->amp = 0.0f;
    m->freq_hz = 0.0f;
    m->crossings = 0;
    m->sign = 0;
    m->win_t = 0.0f;
    m->amp_first = 0.0f;
    m->amp_last = 0.0f;
    m->seeded = false;
}

void pio_update(PioMonitor *m, float x) {
    float a;
    int s;

    m->trend += (x - m->trend) * (m->dt / TREND_TC);
    m->hp = x - m->trend;

    m->amp *= expf(-m->dt / AMP_TC);
    a = fabsf(m->hp);
    if (a > m->amp) {
        m->amp = a;
    }

    /* Знак міняємо лише коли сигнал вийшов за чверть огинаючої: без
       гістерезису шум коло нуля дав би фантомну «частоту» в сотні герц. */
    if (m->amp > 1e-5f) {
        s = 0;
        if (m->hp > 0.25f * m->amp) {
            s = 1;
        } else if (m->hp < -0.25f * m->amp) {
            s = -1;
        }
        if (s != 0 && s != m->sign) {
            if (m->sign != 0) {
                m->crossings++;
            }
            m->sign = s;
        }
    }

    m->win_t += m->dt;
    if (m->win_t >= WINDOW_SEC) {
        m->freq_hz = (float)m->crossings / (2.0f * m->win_t);
        m->crossings = 0;
        m->win_t = 0.0f;
        if (!m->seeded) {
            m->amp_first = m->amp;
            m->seeded = true;
        }
        m->amp_last = m->amp;
    }
}

float pio_hp(const PioMonitor *m) { return m->hp; }
float pio_amplitude(const PioMonitor *m) { return m->amp; }
float pio_frequency(const PioMonitor *m) { return m->freq_hz; }

float pio_growth(const PioMonitor *m) {
    return (m->amp_first > 1e-4f) ? m->amp_last / m->amp_first : 1.0f;
}

bool pio_active(const PioMonitor *m, float amp_threshold) {
    return m->freq_hz >= 0.5f && m->freq_hz <= 2.5f && m->amp > amp_threshold;
}

void pio_corr_init(PioCorrelator *c, float dt, float window_sec) {
    c->sxy = 0.0f;
    c->sxx = 0.0f;
    c->syy = 0.0f;
    c->leak = expf(-dt / window_sec);
}

void pio_corr_update(PioCorrelator *c, float a, float b) {
    c->sxy = c->sxy * c->leak + a * b;
    c->sxx = c->sxx * c->leak + a * a;
    c->syy = c->syy * c->leak + b * b;
}

float pio_correlation(const PioCorrelator *c) {
    float d = sqrtf(c->sxx * c->syy);
    return d > 1e-9f ? c->sxy / d : 0.0f;
}

float pio_phase_margin(float pm0_deg, float omega_c, float tau) {
    return pm0_deg - (180.0f / PIO_PI) * omega_c * tau;
}

float pio_tau_critical(float pm0_deg, float omega_c) {
    if (omega_c <= 0.0f) {
        return 0.0f;
    }
    return (pm0_deg * PIO_PI / 180.0f) / omega_c;
}
