#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define NUM_CELLS 100000
#define NUM_STATES 8   /* TLC: 8 станів (3 біти/комірку) */

/* Параметри розподілів порогової напруги для 8 станів TLC (у Вольтах) */
static const double STATE_CENTERS[NUM_STATES] = {
    1.20, 1.80, 2.40, 3.00, 3.60, 4.20, 4.80, 5.40
};
static const double BASE_SIGMA = 0.08; /* початкова дисперсія після ISPP */

/* Таблиця коду Ґрея для TLC: Gray(i) -> 3 біти [MSB, CSB, LSB] */
static const unsigned char GRAY_MAP[NUM_STATES] = {
    0x07, 0x06, 0x04, 0x05, 0x01, 0x00, 0x02, 0x03
};

/* Генератор нормально розподіленої випадкової величини (Box-Muller) */
static double rand_gaussian(double mean, double sigma) {
    double u1 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double u2 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * 3.14159265358979323846 * u2);
    return mean + z0 * sigma;
}

/* Моделювання порогової напруги комірки зі зносом P/E та дрейфом витоку */
static double simulate_cell_voltage(int state, int pe_cycles, double retention_hours) {
    /* Знос збільшує сигму розподілу через дефекти оксиду SILC */
    double wear_factor = 1.0 + 0.0003 * sqrt((double)pe_cycles);
    double sigma = BASE_SIGMA * wear_factor;

    /* Витік заряду зміщує напругу вниз (крім стертого стану 0) */
    double drift = 0.0;
    if (state > 0) {
        drift = -0.0005 * state * log(1.0 + retention_hours);
    }

    double nominal = STATE_CENTERS[state];
    return rand_gaussian(nominal + drift, sigma);
}

/* Тверде зчитування стану комірки за 7 опорними напругами */
static int hard_sense_state(double vth) {
    for (int i = 0; i < NUM_STATES - 1; ++i) {
        double v_ref = (STATE_CENTERS[i] + STATE_CENTERS[i + 1]) / 2.0;
        if (vth < v_ref) {
            return i;
        }
    }
    return NUM_STATES - 1;
}

/* Обчислення м'якої метрики LLR для конкретного біта за 7-пороговим стробуванням */
static double compute_soft_llr(double vth, double v_ref_center, double delta_step) {
    /* М'які строби: v_ref_center + [-3Δ, -2Δ, -Δ, 0, +Δ, +2Δ, +3Δ] */
    double diff = vth - v_ref_center;
    double bin_index = floor(diff / delta_step);

    /* Обмеження діапазону індексів бінів [-4 .. +3] */
    if (bin_index < -4.0) bin_index = -4.0;
    if (bin_index > 3.0) bin_index = 3.0;

    /* Перетворення біна на квантовану логарифмічну правдоподібність LLR */
    /* Коефіцієнт масштабування спирається на гаусівську щільність ймовірності */
    double llr = -bin_index * 2.1;
    return llr;
}

int main(void) {
    srand(42);

    int pe_cycles = 1500;
    double retention_hours = 720.0; /* 1 місяць зберігання при кімнатній температурі */

    printf("=== Симулятор зчитування Flash-комірок TLC ===\n");
    printf("Кількість досліджуваних комірок: %d\n", NUM_CELLS);
    printf("Кількість циклів зносу (P/E): %d, Час утримання: %.1f год\n\n", pe_cycles, retention_hours);

    int total_bits = NUM_CELLS * 3;
    int hard_bit_errors = 0;
    double soft_confident_correct = 0;
    double soft_confident_total = 0;

    double soft_delta = 0.035; /* крок м'якого стробування: 35 мВ */

    for (int i = 0; i < NUM_CELLS; ++i) {
        int written_state = rand() % NUM_STATES;
        unsigned char written_bits = GRAY_MAP[written_state];

        double vth = simulate_cell_voltage(written_state, pe_cycles, retention_hours);
        int read_state = hard_sense_state(vth);
        unsigned char read_bits = GRAY_MAP[read_state];

        /* Підрахунок помилок твердого зчитування (Hard Bit Error Rate) */
        for (int b = 0; b < 3; ++b) {
            int bit_w = (written_bits >> b) & 1;
            int bit_r = (read_bits >> b) & 1;
            if (bit_w != bit_r) {
                hard_bit_errors++;
            }
        }

        /* М'яка оцінка для опорного порогу між станами 3 та 4 */
        double v_ref_mid = (STATE_CENTERS[3] + STATE_CENTERS[4]) / 2.0;
        double llr = compute_soft_llr(vth, v_ref_mid, soft_delta);

        /* Якщо оцінка високодостовірна (|LLR| > 5.0), перевіряємо точність */
        if (fabs(llr) > 5.0) {
            soft_confident_total += 1.0;
            bool expected_zero = (written_state >= 4);
            bool predicted_zero = (llr > 0);
            if (expected_zero == predicted_zero) {
                soft_confident_correct += 1.0;
            }
        }
    }

    double rber = (double)hard_bit_errors / (double)total_bits;
    printf("--- Результати моделювання ---\n");
    printf("Помилок твердого читання (Hard Errors): %d з %d бітів\n", hard_bit_errors, total_bits);
    printf("Вхідний рівень помилок (RBER): %.5e (%.3f%%)\n", rber, rber * 100.0);
    printf("Достовірність високопріоритетних бінів LLR (|LLR| > 5.0): %.4f%%\n",
           (soft_confident_correct / soft_confident_total) * 100.0);

    return 0;
}
