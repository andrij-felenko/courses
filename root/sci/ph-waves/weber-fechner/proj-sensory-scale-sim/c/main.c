#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/* Модель Вебера-Фехнера та Стівенса */
typedef struct {
    double i_zero;     /* Абсолютний поріг чутливості I0 */
    double k_weber;    /* Константа Вебера kW (ΔI / I) */
    double k_scale;    /* Масштабний коефіцієнт k */
    double stevens_n;  /* Показник степеня Стівенса n */
} SensoryModel;

/* Захищене обчислення логарифмічного відчуття за Вебером-Фехнером */
double calculate_weber_fechner(const SensoryModel *model, double intensity) {
    if (!model || intensity <= model->i_zero) {
        return 0.0;
    }
    /* Використовуємо log1p для підвищення точності поблизу порогу I0 */
    double delta_ratio = (intensity - model->i_zero) / model->i_zero;
    return model->k_scale * log1p(delta_ratio);
}

/* Обчислення відчуття за степенним законом Стівенса */
double calculate_stevens(const SensoryModel *model, double intensity) {
    if (!model || intensity <= model->i_zero) {
        return 0.0;
    }
    double delta = intensity - model->i_zero;
    return model->k_scale * pow(delta, model->stevens_n);
}

/* Генерація сітки JND ступенів у заданому діапазоні */
int generate_jnd_steps(const SensoryModel *model, double i_max, double *out_buffer, int max_size) {
    if (!model || !out_buffer || model->k_weber <= 0.0) {
        return -1;
    }

    double current_i = model->i_zero;
    int count = 0;

    while (current_i <= i_max && count < max_size) {
        out_buffer[count++] = current_i;
        current_i *= (1.0 + model->k_weber);
    }

    return count;
}

/* Перетворення лінійного світла у 8-бітний sRGB піксель (OETF) */
unsigned char linear_to_srgb_8bit(double linear_val) {
    if (linear_val <= 0.0) return 0;
    if (linear_val >= 1.0) return 255;

    double srgb;
    if (linear_val <= 0.0031308) {
        srgb = 12.92 * linear_val;
    } else {
        srgb = 1.055 * pow(linear_val, 1.0 / 2.4) - 0.055;
    }

    return (unsigned char)(srgb * 255.0 + 0.5);
}

int main(void) {
    SensoryModel vision_model = {
        .i_zero = 1.0e-5,
        .k_weber = 0.01,
        .k_scale = 10.0,
        .stevens_n = 0.33
    };

    printf("=== Моделювання сенсорних шкал (C) ===\n");
    double test_intensities[] = { 1.0e-5, 1.0e-4, 1.0e-3, 1.0e-2, 1.0 };
    size_t num_tests = sizeof(test_intensities) / sizeof(test_intensities[0]);

    for (size_t i = 0; i < num_tests; ++i) {
        double I = test_intensities[i];
        double S_wf = calculate_weber_fechner(&vision_model, I);
        double S_st = calculate_stevens(&vision_model, I);
        printf("I = %10.5f | S_Fechner = %8.4f | S_Stevens = %8.4f\n", I, S_wf, S_st);
    }

    double jnd_buffer[200];
    int steps = generate_jnd_steps(&vision_model, 1.0e-4, jnd_buffer, 200);
    printf("Згенеровано %d JND-ступенів від I0 до 1.0e-4\n", steps);

    printf("\nsRGB квантування яскравості:\n");
    double lum_values[] = { 0.001, 0.01, 0.1, 0.5, 1.0 };
    for (size_t i = 0; i < 5; ++i) {
        unsigned char p = linear_to_srgb_8bit(lum_values[i]);
        printf("Лінійна яскравість = %5.3f -> sRGB 8-bit = %3u\n", lum_values[i], p);
    }

    return 0;
}
