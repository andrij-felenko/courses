/* C implementation: manual memory management, explicit loop processing */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define PI 3.14159265358979323846

typedef struct {
    double fs;          /* Частота дискретизації (Гц) */
    double fc;          /* Несуча частота (Гц) */
    size_t num_samples;
    double *i_baseband;
    double *q_baseband;
    double *passband;
    double *i_recovered;
    double *q_recovered;
} IQModem;

IQModem* iq_modem_create(size_t n, double fs, double fc) {
    IQModem *m = (IQModem*)malloc(sizeof(IQModem));
    if (!m) return NULL;
    m->fs = fs;
    m->fc = fc;
    m->num_samples = n;
    m->i_baseband = (double*)calloc(n, sizeof(double));
    m->q_baseband = (double*)calloc(n, sizeof(double));
    m->passband = (double*)calloc(n, sizeof(double));
    m->i_recovered = (double*)calloc(n, sizeof(double));
    m->q_recovered = (double*)calloc(n, sizeof(double));
    return m;
}

void iq_modem_free(IQModem *m) {
    if (!m) return;
    free(m->i_baseband);
    free(m->q_baseband);
    free(m->passband);
    free(m->i_recovered);
    free(m->q_recovered);
    free(m);
}

/* Up-conversion: Baseband (I, Q) -> Passband s(t) */
void iq_modulate(IQModem *m) {
    double dt = 1.0 / m->fs;
    for (size_t n = 0; n < m->num_samples; n++) {
        double t = n * dt;
        double carrier_i = cos(2.0 * PI * m->fc * t);
        double carrier_q = sin(2.0 * PI * m->fc * t);
        m->passband[n] = m->i_baseband[n] * carrier_i - m->q_baseband[n] * carrier_q;
    }
}

/* Down-conversion з ФНЧ ковзним середнім */
void iq_demodulate(IQModem *m, int filter_len) {
    double dt = 1.0 / m->fs;
    double *i_raw = (double*)malloc(m->num_samples * sizeof(double));
    double *q_raw = (double*)malloc(m->num_samples * sizeof(double));

    /* 1. Множення на квадратурні гетеродини */
    for (size_t n = 0; n < m->num_samples; n++) {
        double t = n * dt;
        i_raw[n] =  2.0 * m->passband[n] * cos(2.0 * PI * m->fc * t);
        q_raw[n] = -2.0 * m->passband[n] * sin(2.0 * PI * m->fc * t);
    }

    /* 2. Низькочастотна фільтрація (ФНЧ) */
    for (size_t n = 0; n < m->num_samples; n++) {
        double sum_i = 0.0, sum_q = 0.0;
        int count = 0;
        for (int k = -filter_len / 2; k <= filter_len / 2; k++) {
            int idx = (int)n + k;
            if (idx >= 0 && idx < (int)m->num_samples) {
                sum_i += i_raw[idx];
                sum_q += q_raw[idx];
                count++;
            }
        }
        m->i_recovered[n] = sum_i / count;
        m->q_recovered[n] = sum_q / count;
    }

    free(i_raw);
    free(q_raw);
}

int main(void) {
    size_t N = 1000;
    double fs = 10000.0; /* 10 кГц */
    double fc = 2000.0;  /* 2 кГц несуча */

    IQModem *m = iq_modem_create(N, fs, fc);
    if (!m) return 1;

    /* Створення низькочастотних сигналів (100 Гц та 50 Гц) */
    for (size_t n = 0; n < N; n++) {
        double t = n / fs;
        m->i_baseband[n] = cos(2.0 * PI * 100.0 * t);
        m->q_baseband[n] = sin(2.0 * PI * 50.0 * t);
    }

    iq_modulate(m);
    iq_demodulate(m, 41);

    printf("Зразок [500]: I_orig=%.4f -> I_rec=%.4f | Q_orig=%.4f -> Q_rec=%.4f\n",
           m->i_baseband[500], m->i_recovered[500],
           m->q_baseband[500], m->q_recovered[500]);

    iq_modem_free(m);
    return 0;
}
