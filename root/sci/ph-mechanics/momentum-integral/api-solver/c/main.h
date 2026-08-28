#ifndef MOMENTUM_SOLVER_H
#define MOMENTUM_SOLVER_H

#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BL_SUCCESS = 0,
    BL_ERROR_NULL_POINTER = -1,
    BL_ERROR_INVALID_GRID = -2,
    BL_ERROR_INVALID_VISCOSITY = -3,
    BL_ERROR_SEPARATION = -4,
    BL_ERROR_CONVERGENCE = -5
} bl_status_t;

typedef enum {
    BL_MODE_THWAITES_LAMINAR = 0,
    BL_MODE_POHLHAUSEN_LAMINAR = 1,
    BL_MODE_HEAD_TURBULENT = 2,
    BL_MODE_COUPLED_TRANSITION = 3
} bl_solver_mode_t;

typedef struct {
    double density;              /* Густина флюїду rho, [кг/м³] */
    double kinematic_viscosity;  /* Кінематична в'язкість nu, [м²/с] */
    double reynolds_critical;    /* Критичне число Рейнольдса переходу */
} bl_fluid_properties_t;

typedef struct {
    bl_solver_mode_t mode;       /* Алгоритм розв'язання */
    int enable_separation_stop;  /* Зупиняти розрахунок при відриві (1 - так, 0 - ні) */
    double initial_theta;        /* Початкова товщина втрати імпульсу, [м] */
} bl_solver_config_t;

typedef struct {
    double x;                    /* Поздовжня координата, [м] */
    double U_e;                  /* Зовнішня швидкість, [м/с] */
    double dUe_dx;               /* Градієнт швидкості, [1/с] */
    double theta;                /* Товщина втрати імпульсу, [м] */
    double delta_star;           /* Товщина зміщення, [м] */
    double H;                    /* Коефіцієнт форми (delta_star / theta) */
    double C_f;                  /* Коефіцієнт поверхневого тертя */
    double tau_w;                /* Напруження тертя на стінці, [Па] */
    int is_separated;            /* 1 якщо в цій точці спостерігається відрив */
    int is_turbulent;            /* 1 якщо режим течії турбулентний */
} bl_point_result_t;

typedef struct {
    bl_point_result_t *points;   /* Динамічний масив результатів */
    size_t count;                /* Кількість оброблених точок */
    double x_separation;         /* Координата відриву (якщо стався, інакше -1.0) */
    double total_friction_drag;  /* Сумарний опір тертя на один метр ширини, [Н/м] */
} bl_solution_mesh_t;

/**
 * @brief Ініціалізація конфігурації розв'язувача за замовчуванням
 */
bl_status_t bl_config_init_default(bl_solver_config_t *config);

/**
 * @brief Виконання розрахунку примежового шару уздовж заданої сітки
 * 
 * @param fluid Параметри середовища (густина, в'язкість)
 * @param config Налаштування розв'язувача
 * @param x_grid Масив координат точок x, [м]
 * @param U_e_grid Масив зовнішніх швидкостей, [м/с]
 * @param dUe_dx_grid Масив градієнтів швидкостей, [1/с]
 * @param n_points Кількість точок сітки
 * @param out_mesh Структура для запису вихідних результатів
 * @return bl_status_t Код завершення розрахунку
 */
bl_status_t bl_solve_boundary_layer(
    const bl_fluid_properties_t *fluid,
    const bl_solver_config_t *config,
    const double *x_grid,
    const double *U_e_grid,
    const double *dUe_dx_grid,
    size_t n_points,
    bl_solution_mesh_t *out_mesh
);

/**
 * @brief Звільнення пам'яті вихідної сітки результатів
 */
void bl_mesh_free(bl_solution_mesh_t *mesh);

/**
 * @brief Отримання текстового опису коду статусу
 */
const char* bl_status_to_string(bl_status_t status);

#ifdef __cplusplus
}
#endif

#endif /* MOMENTUM_SOLVER_H */
