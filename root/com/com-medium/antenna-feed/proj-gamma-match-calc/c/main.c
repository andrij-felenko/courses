#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Вхідна структура даних геометричних та частотних параметрів */
typedef struct {
    double freq_mhz;       /* Робоча частота в МГц */
    double target_z0;      /* Хвильовий опір фідера (напр. 50 Ом) */
    double r_ant;          /* Активний опір вібратора антени (Ом) */
    double r_element_mm;   /* Радіус випромінювального елемента (мм) */
    double r_rod_mm;       /* Радіус гама-стрижня (мм) */
    double spacing_mm;     /* Відстань між осями елемента і стрижня (мм) */
} gamma_input_t;

/* Вихідна структура з розрахованими параметрами узгодження */
typedef struct {
    double u_ratio;        /* Коефіцієнт розподілу струму u */
    double step_up_m;      /* Коефіцієнт трансформації опору m = (1+u)^2 */
    double z0_loop;        /* Хвильовий опір гама-шлейфу (Ом) */
    double x_loop;         /* Індуктивна реактивність шлейфу (Ом) */
    double gamma_len_cm;   /* Необхідна довжина гама-стрижня L_γ (см) */
    double c_gamma_pf;     /* Ємність компенсаційного конденсатора C_γ (пФ) */
    double balun_l_uh;     /* Мін. індуктивність дроселя балуна для Z_cm >= 500 Ом (мкГн) */
} gamma_output_t;

/**
 * Виконує повний розрахунок параметрів гама-узгоджувача.
 * Повертає true у разі успіху, false при нестійких або некоректних даних.
 */
bool calculate_gamma_match(const gamma_input_t *in, gamma_output_t *out) {
    if (!in || !out) {
        return false;
    }

    /* Валідація фізичних меж параметрів */
    if (in->freq_mhz <= 0.0 || in->r_ant <= 0.0 || 
        in->r_element_mm <= 0.0 || in->r_rod_mm <= 0.0 || 
        in->spacing_mm <= (in->r_element_mm + in->r_rod_mm)) {
        return false;
    }

    const double c_speed = 299.792458; // Швидкість світла Мм/с
    double lambda_m = c_speed / in->freq_mhz; // Довжина хвилі у метрах
    
    // 1. Обчислення розкладу струму u та коефіцієнта m
    out->u_ratio = log(in->spacing_mm / in->r_rod_mm) / log(in->spacing_mm / in->r_element_mm);
    out->step_up_m = (1.0 + out->u_ratio) * (1.0 + out->u_ratio);

    double r_transformed = out->step_up_m * in->r_ant;
    if (r_transformed < in->target_z0) {
        /* Геометрія не забезпечує необхідного підйому опору до Z0 */
        return false;
    }

    // 2. Хвильовий опір двопровідного шлейфу Z0_loop
    out->z0_loop = 120.0 * log(in->spacing_mm / sqrt(in->r_element_mm * in->r_rod_mm));

    // 3. Індуктивна реактивність X_loop
    double ratio = r_transformed / in->target_z0;
    out->x_loop = r_transformed * sqrt(ratio - 1.0);

    // 4. Геометрична довжина шлейфу L_γ у сантиметрах
    double tan_val = out->x_loop / out->z0_loop;
    double beta_l = atan(tan_val);
    double l_gamma_m = (beta_l * lambda_m) / (2.0 * M_PI);
    out->gamma_len_cm = l_gamma_m * 100.0;

    // 5. Послідовний компенсаційний конденсатор C_γ у пікофарадах
    double omega = 2.0 * M_PI * in->freq_mhz * 1e6;
    out->c_gamma_pf = (1.0 / (omega * out->x_loop)) * 1e12;

    // 6. Струмовий балун: мінімальна індуктивність L_cm для Z_cm >= 500 Ом
    const double target_z_cm = 500.0;
    out->balun_l_uh = (target_z_cm / omega) * 1e6;

    return true;
}

int main(void) {
    gamma_input_t input = {
        .freq_mhz = 144.2,
        .target_z0 = 50.0,
        .r_ant = 18.0,
        .r_element_mm = 6.0,
        .r_rod_mm = 2.0,
        .spacing_mm = 45.0
    };
    gamma_output_t output;

    printf("=== Інженерний калькулятор гама-узгоджувача (C11 implementation) ===\n");
    if (calculate_gamma_match(&input, &output)) {
        printf("Частота сигналу : %.2f МГц (λ = %.4f м)\n", input.freq_mhz, 299.792458 / input.freq_mhz);
        printf("Розподіл струму u: %.3f\n", output.u_ratio);
        printf("Коефіцієнт m     : %.3f (підйом опору до %.1f Ом)\n", output.step_up_m, output.step_up_m * input.r_ant);
        printf("Опір шлейфу Z0g  : %.1f Ом\n", output.z0_loop);
        printf("---------------------------------------------------\n");
        printf("РОЗРАХУНКОВІ ПАРАМЕТРИ ВУЗЛА ЖИВЛЕННЯ:\n");
        printf("Довжина гама-стрижня L_γ   : %.2f см\n", output.gamma_len_cm);
        printf("Ємність конденсатора C_γ    : %.2f пФ\n", output.c_gamma_pf);
        printf("Мін. індуктивність балуна L : %.3f мкГн (для Z_cm >= 500 Ом)\n", output.balun_l_uh);
    } else {
        printf("Помилка: Задані геометричні параметри не дозволяють виконати узгодження.\n");
    }

    return 0;
}
