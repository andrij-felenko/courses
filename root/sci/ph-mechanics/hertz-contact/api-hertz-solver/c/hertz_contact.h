/* 
 * hertz_contact.h — C API для розрахунку контакту Герца
 */

#ifndef HERTZ_CONTACT_H
#define HERTZ_CONTACT_H

#ifdef __cplusplus
extern "C" {
#endif

/* Коди помилок виконання */
typedef enum {
    HERTZ_SUCCESS = 0,
    HERTZ_ERR_INVALID_PARAM = -1,
    HERTZ_ERR_GEOMETRY_SINGULAR = -2,
    HERTZ_ERR_MATERIAL_OUT_OF_BOUNDS = -3,
    HERTZ_ERR_NULL_POINTER = -4
} hertz_error_t;

/* Фізичні властивості ізотропного матеріалу */
typedef struct {
    double E;    /* Модуль пружності першого роду / модуль Юнга (Па) */
    double nu;   /* Коефіцієнт поперечної деформації / Пуассона (0 <= nu < 0.5) */
} hertz_material_t;

/* Результати розрахунку точкового (сферичного) контакту */
typedef struct {
    double R_star;   /* Зведений радіус кривини (м) */
    double E_star;   /* Зведений модуль пружності (Па) */
    double a;        /* Радіус кругової плями контакту (м) */
    double delta;    /* Глибина втискання / сумарне зближення центрів (м) */
    double p0;       /* Максимальний контактний тиск у центрі (Па) */
    double p_mean;   /* Середній контактний тиск (Па) */
    double area;     /* Площа поверхні контакту (м²) */
    double z_peak;   /* Глибина розташування піку зсувного напруження (м) */
    double tau_max;  /* Значення максимального зсувного напруження (Па) */
} hertz_sphere_result_t;

/* Результати розрахунку лінійного (циліндричного) контакту */
typedef struct {
    double R_star;   /* Зведений радіус кривини (м) */
    double E_star;   /* Зведений модуль пружності (Па) */
    double b;        /* Півширина прямокутної плями контакту (м) */
    double delta;    /* Зближення поверхонь циліндрів (м) */
    double p0;       /* Максимальний тиск по осьовій лінії (Па) */
    double p_mean;   /* Середній тиск по площі прямокутника (Па) */
    double area;     /* Площа поверхні контакту 2b * L (м²) */
} hertz_cylinder_result_t;

/* Точка зрізу поля напружень по глибині z */
typedef struct {
    double z;          /* Глибина під поверхнею контакту (м) */
    double z_over_a;   /* Безрозмірна глибина z / a */
    double sigma_z;    /* Головне осьове стискальне напруження (Па) */
    double sigma_x;    /* Головне радіальне стискальне напруження (Па) */
    double tau_max;    /* Максимальне зсувне напруження (Па) */
} hertz_stress_point_t;

/* 
 * Обчислення зведеного радіуса кривини: 1/R* = 1/R1 + 1/R2
 * Приймає радіуси R1 та R2 (м). Для площини передається INFINITY або велике число.
 * Повертає R* (м) або 0.0 при помилці.
 */
double hertz_calc_r_star(double R1, double R2);

/* 
 * Обчислення зведеного модуля пружності: 1/E* = (1-nu1^2)/E1 + (1-nu2^2)/E2
 * Повертає E* (Па) або 0.0 при некоректних матеріалах.
 */
double hertz_calc_e_star(hertz_material_t mat1, hertz_material_t mat2);

/*
 * Солвер сферичного герцівського контакту
 * Параметри:
 *   F    - нормальна сила стискання (Н), має бути > 0
 *   R1   - радіус кривини першого тіла (м)
 *   R2   - радіус кривини другого тіла (м)
 *   mat1 - матеріальні властивості першого тіла
 *   mat2 - матеріальні властивості другого тіла
 *   out  - вказівник на структуру результатів
 * Повертає HERTZ_SUCCESS (0) або код помилки hertz_error_t.
 */
hertz_error_t hertz_solve_sphere(double F, double R1, double R2,
                                 hertz_material_t mat1, hertz_material_t mat2,
                                 hertz_sphere_result_t *out);

/*
 * Солвер циліндричного герцівського контакту
 * Параметри:
 *   F    - нормальна сила стискання (Н)
 *   L    - активна довжина контакту циліндрів (м)
 *   R1, R2 - радіуси кривини циліндрів (м)
 *   mat1, mat2 - властивості матеріалів
 *   out  - вказівник на результат
 */
hertz_error_t hertz_solve_cylinder(double F, double L, double R1, double R2,
                                   hertz_material_t mat1, hertz_material_t mat2,
                                   hertz_cylinder_result_t *out);

/*
 * Обчислення профілю напружень вздовж осі z під центром сферичного контакту
 * Параметри:
 *   sph     - результати сферичного контакту
 *   z_max   - максимальна глибина розрахунку (м)
 *   steps   - кількість кроків дискретизації
 *   out_arr - вихідний масив розміром (steps + 1)
 */
hertz_error_t hertz_calc_stress_profile(const hertz_sphere_result_t *sph,
                                        double z_max, int steps,
                                        hertz_stress_point_t *out_arr);

#ifdef __cplusplus
}
#endif

#endif /* HERTZ_CONTACT_H */
