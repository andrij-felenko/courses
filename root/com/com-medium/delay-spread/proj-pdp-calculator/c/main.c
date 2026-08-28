#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <complex.h>

#define MAX_RAYS 16
#define SYMBOL_COUNT 1000
#define FFT_SIZE 64
#define CP_SIZE 16

typedef struct {
    double delay_ns;     /* Затримка променя в наносекундах */
    double power_linear; /* Лінійна потужність променя */
    double phase_rad;    /* Фаза променя в радіанах */
} multipath_ray_t;

typedef struct {
    double total_power;   /* Сумарна потужність */
    double mean_delay_ns; /* Середня затримка τ̄ (нс) */
    double rms_spread_ns; /* RMS delay spread σ_τ (нс) */
    double bc_50_mhz;     /* Смуга когерентності B_c (50%), МГц */
    double bc_90_mhz;     /* Смуга когерентності B_c (90%), МГц */
    bool is_flat_fading;  /* true якщо B_s < B_c */
} pdp_metrics_t;

/* Обчислення метрик PDP каналу */
bool calculate_pdp_metrics(const multipath_ray_t *rays, size_t count, 
                          double signal_bw_mhz, pdp_metrics_t *out) 
{
    if (!rays || count == 0 || !out) {
        return false;
    }

    double p_total = 0.0;
    double weighted_delay_sum = 0.0;
    double weighted_delay_sq_sum = 0.0;

    for (size_t i = 0; i < count; ++i) {
        double p = rays[i].power_linear;
        double t = rays[i].delay_ns;
        if (p < 0.0 || t < 0.0) {
            return false; /* Некоректні дані */
        }
        p_total += p;
        weighted_delay_sum += p * t;
        weighted_delay_sq_sum += p * t * t;
    }

    if (p_total <= 0.0) {
        return false;
    }

    double tau_mean = weighted_delay_sum / p_total;
    double tau_sq_mean = weighted_delay_sq_sum / p_total;
    double variance = tau_sq_mean - (tau_mean * tau_mean);

    double rms_spread = (variance > 0.0) ? sqrt(variance) : 0.0;

    out->total_power = p_total;
    out->mean_delay_ns = tau_mean;
    out->rms_spread_ns = rms_spread;

    if (rms_spread > 0.0) {
        /* B_c (МГц) = 1000 / (factor * rms_ns) */
        out->bc_50_mhz = 1000.0 / (5.0 * rms_spread);
        out->bc_90_mhz = 1000.0 / (50.0 * rms_spread);
    } else {
        out->bc_50_mhz = 1e9;
        out->bc_90_mhz = 1e9;
    }

    out->is_flat_fading = (signal_bw_mhz < out->bc_50_mhz);
    return true;
}

/* Дискретна згортка сигналу з променями каналу (моделювання ISI) */
void simulate_channel_isi(const double complex *in_symbols, size_t num_symbols,
                         const multipath_ray_t *rays, size_t num_rays,
                         double symbol_duration_ns, double complex *out_symbols)
{
    for (size_t n = 0; n < num_symbols; ++n) {
        double complex rx_sample = 0.0 + 0.0 * I;
        
        for (size_t r = 0; r < num_rays; ++r) {
            /* Відносна затримка у символьних інтервалах */
            double ray_delay_sym = rays[r].delay_ns / symbol_duration_ns;
            int tap_delay = (int)floor(ray_delay_sym + 0.5);
            
            if ((int)n >= tap_delay) {
                double amp = sqrt(rays[r].power_linear);
                double complex phase_rot = cexp(I * rays[r].phase_rad);
                rx_sample += in_symbols[n - tap_delay] * amp * phase_rot;
            }
        }
        out_symbols[n] = rx_sample;
    }
}

/* Оцінка частоти помилок символів (SER) для QPSK */
double calculate_qpsk_ser(const double complex *tx, const double complex *rx, size_t count) {
    size_t errors = 0;
    for (size_t i = 0; i < count; ++i) {
        /* Демодуляція за знаками Re та Im */
        int tx_re = (creal(tx[i]) > 0) ? 1 : -1;
        int tx_im = (cimag(tx[i]) > 0) ? 1 : -1;
        
        int rx_re = (creal(rx[i]) > 0) ? 1 : -1;
        int rx_im = (cimag(rx[i]) > 0) ? 1 : -1;

        if (tx_re != rx_re || tx_im != rx_im) {
            errors++;
        }
    }
    return (double)errors / (double)count;
}

int main(void) {
    /* 1. Модель каналу ITU-R Vehicular A */
    multipath_ray_t veh_a_profile[] = {
        {   0.0, 1.000, 0.00 }, /* 0 дБ */
        { 310.0, 0.794, 0.85 }, /* -1 дБ */
        { 710.0, 0.126, 1.42 }, /* -9 дБ */
        {1090.0, 0.032, 2.10 }, /* -15 дБ */
        {1730.0, 0.010, 2.85 }, /* -20 дБ */
        {2510.0, 0.003, 3.14 }  /* -25 дБ */
    };
    size_t num_rays = sizeof(veh_a_profile) / sizeof(veh_a_profile[0]);

    printf("=== КАЛЬКУЛЯТОР ПРОФІЛЮ ЗАТРИМОК ТА СИМУЛЯТОР ISI (C) ===\n\n");

    pdp_metrics_t metrics;
    if (calculate_pdp_metrics(veh_a_profile, num_rays, 20.0, &metrics)) {
        printf("Повна потужність P_total: %.3f\n", metrics.total_power);
        printf("Середня затримка (tau_bar): %.2f нс\n", metrics.mean_delay_ns);
        printf("RMS Delay Spread (sigma_tau): %.2f нс\n", metrics.rms_spread_ns);
        printf("Смуга когерентності B_c (50%%): %.3f МГц\n", metrics.bc_50_mhz);
        printf("Смуга когерентності B_c (90%%): %.3f МГц\n", metrics.bc_90_mhz);
        printf("Режим для B_s = 20.0 МГц: %s\n\n", 
               metrics.is_flat_fading ? "Плоске завмирання" : "Частотно-селективне завмирання");
    }

    /* 2. Генерація QPSK символів */
    double complex tx_symbols[SYMBOL_COUNT];
    double complex rx_symbols[SYMBOL_COUNT];
    
    for (int i = 0; i < SYMBOL_COUNT; ++i) {
        double re = (rand() % 2 == 0) ? 1.0 : -1.0;
        double im = (rand() % 2 == 0) ? 1.0 : -1.0;
        tx_symbols[i] = (re + I * im) / sqrt(2.0);
    }

    /* Симуляція повільної передачі (T_s = 10000 нс >> tau_max) */
    simulate_channel_isi(tx_symbols, SYMBOL_COUNT, veh_a_profile, num_rays, 10000.0, rx_symbols);
    double ser_slow = calculate_qpsk_ser(tx_symbols, rx_symbols, SYMBOL_COUNT);
    printf("Повільна передача (T_s = 10 мкс, T_s >> tau_max): QPSK SER = %.4f (Немає ISI)\n", ser_slow);

    /* Симуляція швидкої передачі (T_s = 500 нс < tau_max) */
    simulate_channel_isi(tx_symbols, SYMBOL_COUNT, veh_a_profile, num_rays, 500.0, rx_symbols);
    double ser_fast = calculate_qpsk_ser(tx_symbols, rx_symbols, SYMBOL_COUNT);
    printf("Швидка передача (T_s = 0.5 мкс, T_s < tau_max): QPSK SER = %.4f (Важка ISI!)\n", ser_fast);

    return 0;
}
