#ifndef BEARING_CALC_H
#define BEARING_CALC_H

#include <stdbool.h>

/**
 * @brief Геометричні та механічні параметри мініатюрного підшипника
 */
typedef struct {
    const char *model_name;
    double d_inner_mm;
    double d_outer_mm;
    double width_mm;
    double c_dyn_n;
    double c0_stat_n;
} BearingParams;

/**
 * @brief Параметри посадки з натягом
 */
typedef struct {
    double shaft_interference_um;
    double friction_coeff;
} PressFitParams;

/**
 * @brief Параметри хвилястої пружини для попереднього натягу
 */
typedef struct {
    double free_height_mm;
    double work_height_mm;
    double spring_rate_n_mm;
} WaveSpringParams;

/**
 * @brief Результат розрахунку монтажу
 */
typedef struct {
    double contact_pressure_mpa;
    double press_force_n;
    double preload_force_n;
    double preload_min_rec_n;
    double preload_max_rec_n;
    bool preload_is_safe;
} AssemblyReport;

double calc_contact_pressure_mpa(double d_shaft_mm, double interference_um, double ring_wall_mm);
double calc_press_force_n(double d_shaft_mm, double width_mm, double pressure_mpa, double friction_coeff);
double calc_wave_spring_force_n(const WaveSpringParams *spring);
bool calculate_assembly(const BearingParams *bearing,
                        const PressFitParams *fit,
                        const WaveSpringParams *spring,
                        AssemblyReport *out_report);

#endif /* BEARING_CALC_H */
