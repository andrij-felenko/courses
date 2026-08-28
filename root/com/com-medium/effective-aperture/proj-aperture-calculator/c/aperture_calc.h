/* aperture_calc.h — Професійний калькулятор апертури антени (C99/C11) */
#ifndef APERTURE_CALC_H
#define APERTURE_CALC_H

#include <math.h>
#include <stdbool.h>
#include <stdio.h>

#define SPEED_OF_LIGHT 299792458.0 /* швидкість світла у вакуумі, м/с */
#define M_PI_CONST     3.14159265358979323846

/* Структура вхідних параметрів антени */
typedef struct {
    double frequency_hz;   /* Частота сигналу у Гц (f > 0) */
    double gain_dbi;       /* Підсилення антени у дБі */
    double efficiency;     /* Коефіцієнт ефективності η_a (0.0 ... 1.0) */
} antenna_params_t;

/* Структура розрахованих результатів */
typedef struct {
    double wavelength_m;      /* Довжина хвилі λ, м */
    double effective_area_m2; /* Ефективна апертура A_e, м² */
    double physical_area_m2;  /* Фізична площа A_phys (якщо η_a > 0), м² */
    double dish_diameter_m;   /* Еквівалентний діаметр параболи D, м */
} aperture_result_t;

/* Перелічення кодів помилок */
typedef enum {
    APERTURE_OK = 0,
    APERTURE_ERR_NULL_PTR,
    APERTURE_ERR_INVALID_FREQ,
    APERTURE_ERR_INVALID_EFFICIENCY
} aperture_error_t;

/**
 * @brief Обчислює параметри ефективної та фізичної апертури антени.
 * @param params Вказівник на вхідні параметри антени.
 * @param result Вказівник на структуру для запису результатів.
 * @return Код помилки APERTURE_OK у разі успіху.
 */
aperture_error_t calculate_aperture(const antenna_params_t* params, aperture_result_t* result) {
    if (!params || !result) {
        return APERTURE_ERR_NULL_PTR;
    }
    if (params->frequency_hz <= 0.0) {
        return APERTURE_ERR_INVALID_FREQ;
    }
    if (params->efficiency < 0.0 || params->efficiency > 1.0) {
        return APERTURE_ERR_INVALID_EFFICIENCY;
    }

    /* 1. Обчислюємо довжину хвилі λ = c / f */
    double lambda = SPEED_OF_LIGHT / params->frequency_hz;

    /* 2. Лінеаризуємо підсилення: G_linear = 10^(G_dBi / 10) */
    double g_linear = pow(10.0, params->gain_dbi / 10.0);

    /* 3. Ефективна апертура A_e = (λ² / 4π) · G_linear */
    double a_e = (lambda * lambda / (4.0 * M_PI_CONST)) * g_linear;

    result->wavelength_m = lambda;
    result->effective_area_m2 = a_e;

    /* 4. Фізичні розміри за наявності ефективності η_a > 0 */
    if (params->efficiency > 0.0) {
        result->physical_area_m2 = a_e / params->efficiency;
        result->dish_diameter_m = sqrt(4.0 * result->physical_area_m2 / M_PI_CONST);
    } else {
        result->physical_area_m2 = 0.0;
        result->dish_diameter_m = 0.0;
    }

    return APERTURE_OK;
}

/**
 * @brief Обчислює прийняту потужність від густини потоку S (Вт/м²).
 */
double calculate_received_power_watts(double power_density_w_m2, double effective_area_m2) {
    if (power_density_w_m2 < 0.0 || effective_area_m2 < 0.0) {
        return 0.0;
    }
    return power_density_w_m2 * effective_area_m2;
}

#endif /* APERTURE_CALC_H */
