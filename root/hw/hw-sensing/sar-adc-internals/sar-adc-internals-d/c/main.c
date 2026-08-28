#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#define ADC_BITS 12
#define CDAC_SIZE (1 << ADC_BITS)

typedef struct {
    double vref;           /* Опорна напруга, В */
    double c_unit;         /* Одинична ємність C0, Ф */
    double c_sample_tot;   /* Сумарна ємність C_total, Ф */
    double r_total;        /* Сумарний опір кола заряду, Ом */
    double t_acq;          /* Час вибірки, с */
    double comp_offset;    /* Напруга зсуву компаратора, В */
    double comp_noise_rms; /* СРК шуму компаратора, В */
    double temp_k;         /* Температура, Кельвін */
    double cap_weights[ADC_BITS]; /* Реальні ваги ємностей з урахуванням розкиду */
} SarAdcModel;

/* Генератор нормально розподіленого шуму (перетворення Бокса-Мюллера) */
static double generate_gaussian(double mean, double sigma) {
    double u1 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double u2 = ((double)rand() + 1.0) / ((double)RAND_MAX + 1.0);
    double z0 = sqrt(-2.0 * log(u1)) * cos(2.0 * 3.14159265358979323846 * u2);
    return mean + z0 * sigma;
}

/* Ініціалізація моделі АЦП з розкидом параметрів кремнію */
void sar_adc_init(SarAdcModel* adc, double vref, double r_src, double t_acq, double cap_mismatch_std) {
    adc->vref = vref;
    adc->c_unit = 25e-15; /* 25 фФ */
    adc->r_total = r_src + 1500.0; /* Rsrc + R_switch */
    adc->t_acq = t_acq;
    adc->comp_offset = 0.0004; /* 400 мкВ зсуву */
    adc->comp_noise_rms = 0.00015; /* 150 мкВ шуму */
    adc->temp_k = 300.0;

    double c_accum = 0.0;
    for (int i = 0; i < ADC_BITS; i++) {
        double ideal_weight = (double)(1 << i);
        /* Розкид ємності згідно із законом Пелгрома sigma ~ 1/sqrt(Area) */
        double sigma = cap_mismatch_std / sqrt(ideal_weight);
        double actual_weight = ideal_weight * (1.0 + generate_gaussian(0.0, sigma));
        adc->cap_weights[i] = actual_weight;
        c_accum += actual_weight * adc->c_unit;
    }
    c_accum += 1.0 * adc->c_unit; /* Dummy capacitor 1C */
    adc->c_sample_tot = c_accum;
}

/* Виконання одного повного циклу аналого-цифрового перетворення */
unsigned int sar_adc_convert(const SarAdcModel* adc, double v_in) {
    /* 1. Фаза вибірки: експоненційний заряд Csample */
    double tau = adc->r_total * adc->c_sample_tot;
    double settling_factor = 1.0 - exp(-adc->t_acq / tau);
    double v_sampled = v_in * settling_factor;

    /* 2. Тепловий шум комутації kT/C */
    const double kb = 1.380649e-23;
    double kt_c_noise_sigma = sqrt((kb * adc->temp_k) / adc->c_sample_tot);
    v_sampled += generate_gaussian(0.0, kt_c_noise_sigma);

    /* 3. Фіксація: інверсія потенціалу на плаваючому вузлі Vx */
    double v_x = -v_sampled;
    unsigned int digital_code = 0;

    /* 4. Порозрядне зважування (Binary Search від MSB до LSB) */
    double c_tot_weights = (double)(1 << ADC_BITS);

    for (int bit = ADC_BITS - 1; bit >= 0; bit--) {
        /* Пробне підключення поточної ємності до Vref */
        double v_trial_step = adc->vref * (adc->cap_weights[bit] / c_tot_weights);
        double v_x_probe = v_x + v_trial_step;

        /* Врахування зсуву та шуму стробування компаратора */
        double comp_threshold = adc->comp_offset + generate_gaussian(0.0, adc->comp_noise_rms);

        if (v_x_probe < comp_threshold) {
            /* Сигнал більший за пробний рівень: біт = 1 */
            digital_code |= (1 << bit);
            v_x = v_x_probe; /* Залишаємо нижню обкладку на Vref */
        } else {
            /* Сигнал менший: біт = 0 (скидаємо обкладку на GND) */
            /* v_x залишається без доданого кроку */
        }
    }

    return digital_code;
}

int main(void) {
    SarAdcModel adc;
    sar_adc_init(&adc, 3.3, 10000.0, 1.2e-6, 0.002);

    printf("=== Симуляція SAR АЦП 12-біт (Vref = 3.3 В) ===\n");
    double test_voltages[] = {0.0, 0.825, 1.650, 2.475, 3.300};
    for (int i = 0; i < 5; i++) {
        double v = test_voltages[i];
        unsigned int code = sar_adc_convert(&adc, v);
        double reconstructed_v = (code * adc.vref) / (double)(CDAC_SIZE - 1);
        printf("Вхід: %6.4f В -> Код: %4u -> Відновлено: %6.4f В (Похибка: %+6.2f мВ)\n",
               v, code, reconstructed_v, (reconstructed_v - v) * 1000.0);
    }
    return 0;
}
