/* C API: Rigid Body Types and Structures (C99 / C11) */
#ifndef RIGID_BODY_API_H
#define RIGID_BODY_API_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/** @brief Тривимірний вектор подвійної точності (24 байти) */
typedef struct {
    double x;
    double y;
    double z;
} rb_vec3_t;

/** @brief Одиничний кватерніон орієнтації [w, x, y, z] (32 байти) */
typedef struct {
    double w;
    double x;
    double y;
    double z;
} rb_quat_t;

/** @brief Симетрична матриця 3x3 у формі плоского масиву (72 байти) */
typedef struct {
    double m[3][3];
} rb_mat3_t;

/**
 * @brief Повний вектор стану абсолютно твердого тіла (104 байти)
 */
typedef struct {
    rb_vec3_t position;         /**< Позиція центру мас у світовій системі (m) */
    rb_vec3_t linear_velocity;  /**< Поступальна швидкість у світовій системі (m/s) */
    rb_quat_t orientation;      /**< Орієнтація у вигляді одиничного кватерніона */
    rb_vec3_t angular_velocity; /**< Кутова швидкість у ВЛАСНІЙ системі тіла (rad/s) */
} rb_state_t;

/**
 * @brief Масо-інерційні характеристики твердого тіла
 */
typedef struct {
    double mass;                /**< Загальна маса тіла (kg), повинна бути > 0 */
    rb_vec3_t inertia_diag;     /**< Головні моменти інерції [I_xx, I_yy, I_zz] (kg·m²) */
    rb_vec3_t inv_inertia_diag; /**< Обернені моменти інерції [1/I_xx, 1/I_yy, 1/I_zz] */
    rb_vec3_t center_of_mass;   /**< Зсув центру мас відносно геометричного центру (m) */
} rb_mass_props_t;

/**
 * @brief Вхідні зовнішні силові фактори
 */
typedef struct {
    rb_vec3_t force_world;      /**< Результуюча сила у світовій системі (N) */
    rb_vec3_t torque_body;      /**< Результуючий момент у ВЛАСНІЙ системі (N·m) */
} rb_inputs_t;

/**
 * @brief Похідні фізичні величини стану тіла
 */
typedef struct {
    double kinetic_energy_trans; /**< Поступальна кінетична енергія (J) */
    double kinetic_energy_rot;   /**< Обертальна кінетична енергія (J) */
    double kinetic_energy_total; /**< Повна кінетична енергія (J) */
    rb_vec3_t linear_momentum;   /**< Повний лінійний імпульс у світовій системі (kg·m/s) */
    rb_vec3_t angular_momentum;  /**< Повний момент імпульсу у світовій системі (kg·m²/s) */
    rb_mat3_t inertia_world;     /**< Тензор інерції, трансформований у світову систему */
} rb_derived_t;

/** @brief Перерахований тип кодів помилок верифікації стану */
typedef enum {
    RB_OK = 0,
    RB_ERROR_INVALID_MASS = 1,
    RB_ERROR_INVALID_INERTIA = 2,
    RB_ERROR_QUAT_NOT_NORMALIZED = 3,
    RB_ERROR_NAN_OR_INF = 4
} rb_error_t;

#ifdef __cplusplus
}
#endif

#endif /* RIGID_BODY_API_H */
