/* prandtl_solver.h - C99 public interface for libprandtl */
#ifndef PRANDTL_SOLVER_H
#define PRANDTL_SOLVER_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Типи підтримуваних флюїдів */
typedef enum {
    PRANDTL_FLUID_AIR = 0,
    PRANDTL_FLUID_WATER,
    PRANDTL_FLUID_LIQUID_SODIUM,
    PRANDTL_FLUID_MERCURY,
    PRANDTL_FLUID_ENGINE_OIL,
    PRANDTL_FLUID_ETHANOL
} prandtl_fluid_type_t;

/* Коди помилок API */
typedef enum {
    PRANDTL_SUCCESS = 0,
    PRANDTL_ERR_INVALID_ARGUMENT = -1,
    PRANDTL_ERR_TEMP_OUT_OF_RANGE = -2,
    PRANDTL_ERR_PRESSURE_OUT_OF_RANGE = -3,
    PRANDTL_ERR_CALCULATION_FAILED = -4
} prandtl_error_t;

/* Теплофізичні властивості речовини */
typedef struct {
    double temperature_k;    /* Температура [К] */
    double pressure_pa;       /* Тиск [Па] */
    double density;           /* Густина ρ [кг/м³] */
    double dynamic_viscosity; /* Динамічна в'язкість μ [Па·с] */
    double kin_viscosity;     /* Кінематична в'язкість ν [м²/с] */
    double thermal_cond;      /* Теплопровідність k [Вт/(м·К)] */
    double specific_heat;     /* Теплоємність c_p [Дж/(кг·К)] */
    double thermal_diff;      /* Температуропровідність α [м²/с] */
    double prandtl_number;    /* Число Прандтля Pr [-] */
} prandtl_properties_t;

/* Параметри примежового шару на плоскій пластині */
typedef struct {
    double position_x;        /* Відстань від передньої кромки x [м] */
    double reynolds_x;        /* Місцеве число Рейнольдса Re_x [-] */
    double pecle_x;           /* Місцеве число Пекле Pe_x [-] */
    double delta_v;           /* Товщина гідродинамічного шару δ_v [м] */
    double delta_t;           /* Товщина теплового шару δ_t [м] */
    double ratio_delta;       /* Відношення товщин δ_v / δ_t [-] */
    double skin_friction_cf;  /* Коефіцієнт тертя C_f [-] */
    double nusselt_x;         /* Місцеве число Нуссельта Nu_x [-] */
    double heat_transfer_h;   /* Коефіцієнт тепловіддачі h [Вт/(м²·К)] */
} prandtl_bl_params_t;

/* Публічні функції C API */

/**
 * @brief Обчислити теплофізичні властивості середовища та число Прандтля
 * @param fluid Тип середовища
 * @param temp_k Температура у Кельвінах
 * @param press_pa Статичний тиск у Паскалях
 * @param props Вихідна структура для запису властивостей
 * @return PRANDTL_SUCCESS при успіху, або відповідний код помилки
 */
prandtl_error_t prandtl_get_properties(prandtl_fluid_type_t fluid,
                                       double temp_k,
                                       double press_pa,
                                       prandtl_properties_t *props);

/**
 * @brief Розрахувати параметри примежового шару та тепловіддачі на плоскій пластині
 * @param props Структура властивостей середовища
 * @param velocity_u Швидкість набігаючого потоку U [м/с]
 * @param position_x Відстань від носка пластини x [м]
 * @param bl_out Вихідна структура результатів
 * @return PRANDTL_SUCCESS при успіху
 */
prandtl_error_t prandtl_calc_boundary_layer(const prandtl_properties_t *props,
                                            double velocity_u,
                                            double position_x,
                                            prandtl_bl_params_t *bl_out);

/**
 * @brief Отримати текстовий опис коду помилки
 */
const char* prandtl_strerror(prandtl_error_t err);

#ifdef __cplusplus
}
#endif

#endif /* PRANDTL_SOLVER_H */
