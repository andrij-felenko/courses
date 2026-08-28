#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#define SAMPLE_RATE 8000.0
#define BAUD_RATE   300.0
#define SAMPLES_PER_BIT ((size_t)(SAMPLE_RATE / BAUD_RATE)) // 26 відліків на біт

typedef enum {
    V21_MODE_ORIGINATE, // TX: 980/1180 Гц, RX: 1650/1850 Гц
    V21_MODE_ANSWER     // TX: 1650/1850 Гц, RX: 980/1180 Гц
} V21Mode;

typedef struct {
    V21Mode mode;
    double phase_acc;
    double f_mark;
    double f_space;
} V21Modulator;

typedef struct {
    V21Mode mode;
    double f_mark;
    double f_space;
} V21Demodulator;

void v21_modulator_init(V21Modulator *mod, V21Mode mode) {
    mod->mode = mode;
    mod->phase_acc = 0.0;
    if (mode == V21_MODE_ORIGINATE) {
        mod->f_mark = 980.0;
        mod->f_space = 1180.0;
    } else {
        mod->f_mark = 1650.0;
        mod->f_space = 1850.0;
    }
}

// Модуляція одного біта у масив відліків PCM
void v21_modulate_bit(V21Modulator *mod, uint8_t bit, float *output_samples) {
    double freq = (bit != 0) ? mod->f_mark : mod->f_space;
    double phase_inc = 2.0 * M_PI * freq / SAMPLE_RATE;

    for (size_t i = 0; i < SAMPLES_PER_BIT; i++) {
        output_samples[i] = (float)sin(mod->phase_acc);
        mod->phase_acc += phase_inc;
        if (mod->phase_acc >= 2.0 * M_PI) {
            mod->phase_acc -= 2.0 * M_PI;
        }
    }
}

void v21_demodulator_init(V21Demodulator *demod, V21Mode mode) {
    demod->mode = mode;
    // Приймач працює на протилежній частотній парі відносно передавача
    if (mode == V21_MODE_ORIGINATE) {
        demod->f_mark = 1650.0;
        demod->f_space = 1850.0;
    } else {
        demod->f_mark = 980.0;
        demod->f_space = 1180.0;
    }
}

// Квадратурна демодуляція блоку відліків одного біта
uint8_t v21_demodulate_bit(V21Demodulator *demod, const float *input_samples) {
    double i_mark = 0.0, q_mark = 0.0;
    double i_space = 0.0, q_space = 0.0;

    double omega_mark = 2.0 * M_PI * demod->f_mark / SAMPLE_RATE;
    double omega_space = 2.0 * M_PI * demod->f_space / SAMPLE_RATE;

    for (size_t n = 0; n < SAMPLES_PER_BIT; n++) {
        double sample = (double)input_samples[n];
        
        i_mark += sample * cos(omega_mark * n);
        q_mark += sample * sin(omega_mark * n);

        i_space += sample * cos(omega_space * n);
        q_space += sample * sin(omega_space * n);
    }

    double mag_mark = i_mark * i_mark + q_mark * q_mark;
    double mag_space = i_space * i_space + q_space * q_space;

    return (mag_mark > mag_space) ? 1 : 0;
}

int main(void) {
    V21Modulator mod;
    V21Demodulator demod;

    v21_modulator_init(&mod, V21_MODE_ORIGINATE);
    v21_demodulator_init(&demod, V21_MODE_ANSWER);

    uint8_t test_bits[8] = {1, 0, 1, 1, 0, 0, 1, 0};
    float buffer[SAMPLES_PER_BIT];

    printf("=== V.21 FSK Modem Simulation (C) ===\n");
    printf("Передача 8 бітів на швидкості 300 бод...\n");

    for (int i = 0; i < 8; i++) {
        v21_modulate_bit(&mod, test_bits[i], buffer);
        uint8_t rx_bit = v21_demodulate_bit(&demod, buffer);
        printf("Біт %d: TX = %d -> RX = %d [%s]\n", 
               i, test_bits[i], rx_bit, (test_bits[i] == rx_bit) ? "OK" : "ERROR");
    }

    return 0;
}
