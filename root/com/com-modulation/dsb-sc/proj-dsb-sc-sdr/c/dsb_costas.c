/* dsb_costas.h / dsb_costas.c - C implementation of DSB-SC Modulator & Costas Loop */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

typedef struct {
    double phase;
    double phase_increment; // 2 * PI * f_c / f_s
} dsb_modulator_t;

typedef struct {
    double phase;
    double freq;            // Поточна частота NCO (рад/відлік)
    double alpha;           // Коефіцієнт ФНЧ для I/Q (0..1)
    double kp;              // Пропорційний коефіцієнт петлі
    double ki;              // Інтегральний коефіцієнт петлі
    double lpf_i;           // Стан ФНЧ вітки I
    double lpf_q;           // Стан ФНЧ вітки Q
    double integrator;      // Стан інтегратора петльового фільтра
} costas_loop_t;

void dsb_modulator_init(dsb_modulator_t *mod, double f_carrier, double sample_rate) {
    mod->phase = 0.0;
    mod->phase_increment = 2.0 * M_PI * f_carrier / sample_rate;
}

double dsb_modulate_sample(dsb_modulator_t *mod, double m_sample) {
    double carrier = cos(mod->phase);
    mod->phase += mod->phase_increment;
    if (mod->phase >= 2.0 * M_PI) {
        mod->phase -= 2.0 * M_PI;
    }
    return m_sample * carrier;
}

void costas_loop_init(costas_loop_t *loop, double f_carrier, double sample_rate, 
                      double lpf_cutoff, double damping, double loop_bw) {
    loop->phase = 0.0;
    loop->freq = 2.0 * M_PI * f_carrier / sample_rate;
    
    // Коефіцієнт однополюсного ФНЧ: alpha = dt / (RC + dt)
    double dt = 1.0 / sample_rate;
    double rc = 1.0 / (2.0 * M_PI * lpf_cutoff);
    loop->alpha = dt / (rc + dt);
    
    // Розрахунок коефіцієнтів PI петльового фільтра
    double denom = 1.0 + 2.0 * damping * loop_bw + loop_bw * loop_bw;
    loop->kp = (4.0 * damping * loop_bw) / denom;
    loop->ki = (4.0 * loop_bw * loop_bw) / denom;
    
    loop->lpf_i = 0.0;
    loop->lpf_q = 0.0;
    loop->integrator = 0.0;
}

double costas_demodulate_sample(costas_loop_t *loop, double input_sample) {
    // 1. Генерування квадратурних опорних сигналів NCO
    double nco_i = cos(loop->phase);
    double nco_q = -sin(loop->phase);
    
    // 2. Змішування (перемноження)
    double raw_i = input_sample * nco_i * 2.0;
    double raw_q = input_sample * nco_q * 2.0;
    
    // 3. Низькочастотна фільтрація (ФНЧ I та Q)
    loop->lpf_i += loop->alpha * (raw_i - loop->lpf_i);
    loop->lpf_q += loop->alpha * (raw_q - loop->lpf_q);
    
    // 4. Детектор фазової помилки: e = I * Q
    double error = loop->lpf_i * loop->lpf_q;
    
    // 5. Петльовий PI-фільтр
    loop->integrator += loop->ki * error;
    double control = loop->kp * error + loop->integrator;
    
    // 6. Оновлення фази та частоти NCO
    loop->phase += loop->freq + control;
    while (loop->phase >= 2.0 * M_PI) loop->phase -= 2.0 * M_PI;
    while (loop->phase < 0.0)         loop->phase += 2.0 * M_PI;
    
    // Відновлений аудіосигнал береться з виходу вітки I
    return loop->lpf_i;
}
