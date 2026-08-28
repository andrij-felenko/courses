#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define CELL_COUNT 50000
#define STATE_COUNT 8 /* 8 станів TLC (3 біти/комірку) */

/* Номінальні центри розподілів напруги V_th для станів TLC (Вольти) */
static const double V_CENTERS[STATE_COUNT] = {
    1.25, 1.85, 2.45, 3.05, 3.65, 4.25, 4.85, 5.45
};
static const double INITIAL_SIGMA = 0.075; /* базова дисперсія після ISPP */

/* Відображення коду Ґрея для 8 станів */
static const unsigned char GRAY_TABLE[STATE_COUNT] = {
    0x07, 0x06, 0x04, 0x05, 0x01, 0x00, 0x02, 0x03
};

/* Генерація псевдовипадкового гаусового шуму (метод Бокса — Мюллера) */
static double generate_gaussian(double mean, double sigma) {
    double u1 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double u2 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double z = sqrt(-2.0 * log(u1)) * cos(2.0 * 3.141592653589793 * u2);
    return mean + z * sigma;
}

/* Моделювання порогової напруги комірки з урахуванням зносу та витоку */
static double get_cell_voltage(int state, int pe_cycles, double retention_days) {
    /* Збільшення дисперсії через накопичення дефектів оксиду SILC */
    double wear_sigma = INITIAL_SIGMA * (1.0 + 0.00025 * sqrt((double)pe_cycles));

    /* Дрейф напруги вниз через термоемісію заряду з пастки */
    double drift = 0.0;
    if (state > 0) {
        drift = -0.0004 * (double)state * log(1.0 + retention_days * 24.0);
    }

    return generate_gaussian(V_CENTERS[state] + drift, wear_sigma);
}

/* Тверде зчитування стану за фіксованими компараторами */
static int read_hard_state(double vth) {
    for (int i = 0; i < STATE_COUNT - 1; ++i) {
        double v_ref = (V_CENTERS[i] + V_CENTERS[i + 1]) * 0.5;
        if (vth < v_ref) return i;
    }
    return STATE_COUNT - 1;
}

/* Квантування м'якого відношення правдоподібності LLR біля межі двох станів */
static double calculate_soft_llr(double vth, double v_ref_mid, double delta_step) {
    double delta_v = vth - v_ref_mid;
    double raw_bin = floor(delta_v / delta_step);
    if (raw_bin < -3.0) raw_bin = -3.0;
    if (raw_bin > 2.0) raw_bin = 2.0;

    /* Множник крутизни LLR спирається на густину розподілу ймовірностей */
    return -raw_bin * 2.4;
}

int main(void) {
    srand(12345);

    int pe_cycles = 2500;           /* вичерпаний ресурс циклів перезапису */
    double retention_days = 90.0;   /* 3 місяці зберігання без живлення */
    double soft_delta = 0.035;      /* крок м'якого стробування: 35 мВ */

    printf("=== Симулятор деградації комірок TLC Flash ===\n");
    printf("Кількість комірок: %d, Циклів P/E: %d, Термін зберігання: %.0f діб\n\n",
           CELL_COUNT, pe_cycles, retention_days);

    int total_bits = CELL_COUNT * 3;
    int hard_errors = 0;
    int strong_llr_count = 0;
    int strong_llr_correct = 0;

    double v_boundary = (V_CENTERS[3] + V_CENTERS[4]) * 0.5;

    for (int i = 0; i < CELL_COUNT; ++i) {
        int state_written = rand() % STATE_COUNT;
        unsigned char bits_written = GRAY_TABLE[state_written];

        double vth = get_cell_voltage(state_written, pe_cycles, retention_days);
        int state_read = read_hard_state(vth);
        unsigned char bits_read = GRAY_TABLE[state_read];

        for (int b = 0; b < 3; ++b) {
            if (((bits_written >> b) & 1) != ((bits_read >> b) & 1)) {
                hard_errors++;
            }
        }

        /* М'яка оцінка для центрального порогу перемикання */
        double llr = calculate_soft_llr(vth, v_boundary, soft_delta);
        if (fabs(llr) > 4.5) {
            strong_llr_count++;
            bool bit_is_zero = (state_written >= 4);
            if ((llr > 0) == bit_is_zero) {
                strong_llr_correct++;
            }
        }
    }

    double rber = (double)hard_errors / (double)total_bits;
    printf("Помилок жорсткого читання (Hard Errors): %d з %d бітів\n", hard_errors, total_bits);
    printf("Вхідний рівень помилок (RBER): %.4e (%.3f%%)\n", rber, rber * 100.0);
    printf("Частка високодостовірних LLR: %.2f%%\n", (double)strong_llr_count / CELL_COUNT * 100.0);
    printf("Точність бітів з високим LLR: %.4f%%\n",
           (double)strong_llr_correct / (double)strong_llr_count * 100.0);

    return 0;
}
