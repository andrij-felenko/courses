#ifndef FASTENER_CALC_H
#define FASTENER_CALC_H

#include <stdio.h>
#include <math.h>

/* Структура для опису матеріалу метизу */
typedef struct {
    const char* name;          /* Назва матеріалу/класу міцності */
    double yield_strength;     /* Межа плинності Re (МПа / Н/мм^2) */
    double ultimate_strength;  /* Межа міцності Rm (МПа / Н/мм^2) */
    double young_modulus;      /* Модуль пружності E (МПа / ГПа переведемо в МПа, наприклад 210000) */
} FastenerMaterial;

/* Структура для опису геометричних характеристик різьби */
typedef struct {
    double nominal_diameter;   /* Номінальний діаметр різьби d (мм) */
    double pitch;              /* Крок різьби P (мм) */
    double d2;                 /* Середній діаметр різьби d2 (мм) */
    double d3;                 /* Внутрішній діаметр болта/гвинта d3 (мм) */
    double d_head;             /* Ефективний діаметр опорної поверхні головки болта d_head (мм) */
    double clamped_length;     /* Довжина затиснутої частини L_k (мм) */
} ThreadSpec;

/* Структура для опису коефіцієнтів тертя */
typedef struct {
    double mu_thread;          /* Коефіцієнт тертя в різьбі */
    double mu_bearing;         /* Коефіцієнт тертя під головкою болта */
    double preload_factor;     /* Коефіцієнт попереднього натягу (зазвичай 0.65 - 0.75 від межі плинності) */
} FrictionParams;

/* Прототипи розрахункових функцій */

/**
 * Обчислення розрахункової (напруженої) площі поперечного перерізу різьби As (мм^2)
 * Формула: As = (pi / 4.0) * pow((d2 + d3) / 2.0, 2);
 */
double fastener_calc_stress_area(const ThreadSpec* thread);

/**
 * Обчислення сили попереднього натягу Fp (Н)
 * Формула: F_p = preload_factor * yield_strength * As;
 */
double fastener_calc_preload(const FastenerMaterial* material, const ThreadSpec* thread, const FrictionParams* friction);

/**
 * Обчислення моменту затягування T (Н*м)
 * Формула: T = F_p * (0.16 * pitch + 0.58 * d2 * mu_thread + 0.5 * d_head * mu_bearing); (враховуючи розмірності)
 */
double fastener_calc_tightening_torque(double f_p, const ThreadSpec* thread, const FrictionParams* friction);

/**
 * Обчислення пружного подовження стержня delta L (мм)
 * Формула: delta_L = (F_p * clamped_length) / (young_modulus * As);
 */
double fastener_calc_elongation(double f_p, const FastenerMaterial* material, const ThreadSpec* thread, double as);

/**
 * Обчислення еквівалентного напруження за критерієм фон Мізеса sigma_vm (МПа)
 * Формула: sigma_vm = sqrt(pow(sigma_tension, 2) + 3.0 * pow(tau_torsion, 2));
 */
double fastener_calc_von_mises(double sigma_tension, double tau_torsion);

#endif /* FASTENER_CALC_H */
