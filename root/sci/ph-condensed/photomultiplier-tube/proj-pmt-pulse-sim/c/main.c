#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

typedef struct {
    double quantum_efficiency;
    double dynode_gain;
    int num_dynodes;
    double t_rise_ns;
    double t_fall_ns;
    double dt_ns;
    double noise_sigma_mV;
    double cfd_fraction;
} PMTConfigC;

// Генерація випадкового значення Пуассона
long simulate_poisson_c(double lambda) {
    double L = exp(-lambda);
    double k = 0;
    double p = 1.0;
    do {
        k += 1.0;
        p *= ((double)rand() / RAND_MAX);
    } while (p > L);
    return (long)(k - 1);
}

long simulate_cascade_c(const PMTConfigC* cfg, long num_photoelectrons) {
    long current_electrons = num_photoelectrons;
    for (int d = 0; d < cfg->num_dynodes; ++d) {
        if (current_electrons <= 0) break;
        double mean = (double)current_electrons * cfg->dynode_gain;
        current_electrons = simulate_poisson_c(mean);
    }
    return current_electrons;
}

void generate_pulse_c(const PMTConfigC* cfg, long total_electrons, double total_time_ns, double* voltage, int num_samples) {
    double e_charge = 1.602e-19;
    double Q_coulomb = (double)total_electrons * e_charge;
    double R_load = 50.0;

    for (int i = 0; i < num_samples; ++i) {
        double t = (double)i * cfg->dt_ns;
        double noise = ((double)rand() / RAND_MAX - 0.5) * 2.0 * cfg->noise_sigma_mV;
        if (t > 0.0) {
            double shape = (t / cfg->t_rise_ns) * exp(1.0 - t / cfg->t_rise_ns);
            double current_A = (Q_coulomb / (cfg->t_fall_ns * 1e-9)) * shape;
            voltage[i] = (current_A * R_load * 1000.0) + noise;
        } else {
            voltage[i] = noise;
        }
    }
}

double find_cfd_zero_crossing_c(const PMTConfigC* cfg, const double* waveform, int num_samples) {
    int delay_samples = (int)((cfg->t_rise_ns * (1.0 - cfg->cfd_fraction)) / cfg->dt_ns);
    
    for (int i = 1; i < num_samples; ++i) {
        double delayed1 = ((i - 1) >= delay_samples) ? waveform[(i - 1) - delay_samples] : 0.0;
        double cfd1 = delayed1 - (cfg->cfd_fraction * waveform[i - 1]);

        double delayed2 = (i >= delay_samples) ? waveform[i - delay_samples] : 0.0;
        double cfd2 = delayed2 - (cfg->cfd_fraction * waveform[i]);

        if (cfd1 < 0.0 && cfd2 >= 0.0) {
            double t1 = (double)(i - 1) * cfg->dt_ns;
            double t2 = (double)i * cfg->dt_ns;
            return t1 + (0.0 - cfd1) * (t2 - t1) / (cfd2 - cfd1);
        }
    }
    return -1.0;
}

int main(void) {
    srand((unsigned int)time(NULL));

    PMTConfigC cfg = {0.25, 4.0, 10, 1.2, 3.5, 0.1, 0.5, 0.2};
    long primary_pe = 5;
    long anode_e = simulate_cascade_c(&cfg, primary_pe);

    printf("=== [C] Симуляція імпульсу ФЕУ та CFD ===\n");
    printf("Первинні фотоелектрони: %ld\n", primary_pe);
    printf("Анодний заряд: %ld электронів\n", anode_e);

    int num_samples = 250;
    double voltage[250];
    generate_pulse_c(&cfg, anode_e, 25.0, voltage, num_samples);

    double cfd_time = find_cfd_zero_crossing_c(&cfg, voltage, num_samples);
    printf("CFD час прильоту: %.3f нс\n", cfd_time);

    printf("\nПерші 5 відліків напруги (мВ):\n");
    for (int i = 0; i < 5; ++i) {
        printf("t = %.1f нс: %.2f мВ\n", (double)i * cfg.dt_ns, voltage[i]);
    }

    return 0;
}
