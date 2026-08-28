/* =========================================================================
 * File: poincare_sec.h
 * Description: C99 API for Poincaré map & Monodromy matrix computation
 * ========================================================================= */

#ifndef POINCARE_SEC_H
#define POINCARE_SEC_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* -------------------------------------------------------------------------
 * Переліки та коди помилок
 * ------------------------------------------------------------------------- */

/**
 * @brief Коди повернення функцій API відображення Пуанкаре.
 */
typedef enum {
    POINCARE_SUCCESS                 =  0, /**< Операцію виконано успішно */
    POINCARE_ERROR_NULL_POINTER      = -1, /**< Передано нульовий вказівник */
    POINCARE_ERROR_INVALID_DIMENSION = -2, /**< Некоректна розмірність системи (dim < 1) */
    POINCARE_ERROR_INVALID_PARAM     = -3, /**< Некоректні параметри (крок dt <= 0, tol <= 0) */
    POINCARE_ERROR_DIVERGENCE        = -4, /**< Чисельна розбіжність траєкторії (NaN або Inf) */
    POINCARE_ERROR_MAX_STEPS_EXCEEDED= -5, /**< Перевищено максимальну кількість кроків */
    POINCARE_ERROR_ROOT_FIND_FAILED  = -6, /**< Не вдалося знайти корінь перетину поверхні */
    POINCARE_ERROR_NON_TRANSVERSAL   = -7  /**< Порушено умову трансверсальності (grad_g * f = 0) */
} poincare_status_t;

/**
 * @brief Метод уточнення точки перетину секущої поверхні.
 */
typedef enum {
    POINCARE_ROOT_HENON   = 0, /**< Метод Ено (зміна незалежної змінної на g) */
    POINCARE_ROOT_HERMITE = 1, /**< Кубічна інтерполяція Ерміта з методом Ньютона */
    POINCARE_ROOT_BISECT  = 2  /**< Дихотомія (метод ділення навпіл) */
} poincare_root_method_t;

/* -------------------------------------------------------------------------
 * Типи зворотних викликів (Callbacks)
 * ------------------------------------------------------------------------- */

/**
 * @brief Зворотний виклик для обчислення правої частини диференціальної системи: dx/dt = f(x, t, user_data).
 * 
 * @param dim Розмірність фазового простору системи.
 * @param t Поточний фізичний час.
 * @param state Вказівник на масив поточного стану системи size [dim].
 * @param rhs_out Вказівник на вихідний масив похідних dx/dt size [dim].
 * @param user_data Вказівник на довільні користувацькі параметри (умови, коефіцієнти).
 * @return POINCARE_SUCCESS або код помилки розрахунку.
 */
typedef poincare_status_t (*poincare_rhs_fn)(
    size_t dim,
    double t,
    const double* state,
    double* rhs_out,
    void* user_data
);

/**
 * @brief Зворотний виклик секущої функції g(x) та її градієнта ∇g(x).
 * 
 * @param dim Розмірність фазового простору.
 * @param state Вказівник на масив стану системи.
 * @param val_out Вказівник на вихідне скалярне значення g(state).
 * @param grad_out Вказівник на вихідний масив градієнта ∇g size [dim] (може бути NULL).
 * @param user_data Вказівник на користувацькі дані.
 * @return POINCARE_SUCCESS або код помилки.
 */
typedef poincare_status_t (*poincare_section_fn)(
    size_t dim,
    const double* state,
    double* val_out,
    double* grad_out,
    void* user_data
);

/**
 * @brief Зворотний виклик для обчислення матриці Якобі векторного поля: J[i][j] = df_i / dx_j.
 * 
 * @param dim Розмірність системи.
 * @param t Поточний час.
 * @param state Вказівник на масив стану.
 * @param jac_out Вказівник на вихідну матрицю Якобі розміром [dim * dim] (Row-Major format).
 * @param user_data Користувацькі дані.
 * @return POINCARE_SUCCESS або код помилки.
 */
typedef poincare_status_t (*poincare_jacobian_fn)(
    size_t dim,
    double t,
    const double* state,
    double* jac_out,
    void* user_data
);

/* -------------------------------------------------------------------------
 * Конструкції налаштувань та стану розв'язувача
 * ------------------------------------------------------------------------- */

/**
 * @brief Структура налаштувань чисельного розв'язувача відображення Пуанкаре.
 */
typedef struct {
    double rel_tol;                    /**< Відносна допустима похибка (наприклад, 1e-9) */
    double abs_tol;                    /**< Абсолютна допустима похибка (наприклад, 1e-12) */
    double initial_dt;                 /**< Початковий крок інтегрування dt */
    double max_dt;                     /**< Максимально припустимий крок dt */
    double min_dt;                     /**< Мінімально припустимий крок dt */
    size_t max_steps;                  /**< Максимальна кількість кроків на один перетин */
    poincare_root_method_t root_method;/**< Обраний алгоритм уточнення кореня перетину */
    bool enforce_direction;            /**< Якщо true, враховувати лише перетини з ∇g · f > 0 */
} poincare_config_t;

/**
 * @brief Структура опису точки перетину секущої поверхні.
 */
typedef struct {
    double time;       /**< Фізичний час перетину t* */
    double* state;     /**< Вказівник на виділений буфер стану x(t*) size [dim] */
    double return_time;/**< Час першого повернення T_return = t* - t_prev* */
    size_t step_count; /**< Кількість кроків інтегрування, витрачених на дане повернення */
} poincare_point_t;

/* -------------------------------------------------------------------------
 * Прототипи функцій C API
 * ------------------------------------------------------------------------- */

/**
 * @brief Ініціалізація структури налаштувань конфігурації за замовчуванням.
 * 
 * @param config Вказівник на структуру конфігурації для заповнення.
 * @return POINCARE_SUCCESS у разі успіху.
 */
poincare_status_t poincare_config_init_default(poincare_config_t* config);

/**
 * @brief Обчислення однократного відображення Пуанкаре (наступної точки перетину P(x₀)).
 * 
 * @param dim Розмірність фазового простору системи.
 * @param rhs Зворотний виклик правої частини ЗДРУ.
 * @param section Зворотний виклик секущої поверхні g(x).
 * @param config Налаштування точності розв'язувача.
 * @param t_inout Вказівник на поточний час t (оновлюється значенням t* при поверненні).
 * @param state_inout Масив стану системи size [dim] (оновлюється до P(x)).
 * @param return_time_out Вказівник на вихідну змінну часу повернення (може бути NULL).
 * @param user_data Довільний вказівник користувача, що передається у callbacks.
 * @return POINCARE_SUCCESS при успішному обчисленні точки.
 */
poincare_status_t poincare_step_section(
    size_t dim,
    poincare_rhs_fn rhs,
    poincare_section_fn section,
    const poincare_config_t* config,
    double* t_inout,
    double* state_inout,
    double* return_time_out,
    void* user_data
);

/**
 * @brief Побудова послідовності N точок перерізу Пуанкаре у виділений масив.
 * 
 * @param dim Розмірність системи.
 * @param rhs Зворотний виклик ЗДРУ.
 * @param section Зворотний виклик секущої поверхні.
 * @param config Налаштування точності.
 * @param t0 Початковий час.
 * @param initial_state Початковий фазовий стан size [dim].
 * @param num_points Кількість точок перетину для збору.
 * @param out_states_flat Вихідний плоский масив для точок розміром [num_points * dim].
 * @param out_times Вихідний масив моментів часу розміром [num_points] (може бути NULL).
 * @param user_data Вказівник на користувацькі дані.
 * @return POINCARE_SUCCESS або код помилки.
 */
poincare_status_t poincare_compute_series(
    size_t dim,
    poincare_rhs_fn rhs,
    poincare_section_fn section,
    const poincare_config_t* config,
    double t0,
    const double* initial_state,
    size_t num_points,
    double* out_states_flat,
    double* out_times,
    void* user_data
);

/**
 * @brief Обчислення матриці монодромії M(T) та проектованої матриці Якобі відображення DP(x*).
 * 
 * @param dim Розмірність системи.
 * @param rhs Зворотний виклик ЗДРУ.
 * @param jacobian Зворотний виклик матриці Якобі векторного поля Df.
 * @param config Налаштування розв'язувача.
 * @param period Період T періодичного розв'язку.
 * @param fixed_point Нерухома точка x* size [dim].
 * @param monodromy_out Вихідний масив матриці монодромії size [dim * dim].
 * @param user_data Користувацькі дані.
 * @return POINCARE_SUCCESS або код помилки.
 */
poincare_status_t poincare_compute_monodromy(
    size_t dim,
    poincare_rhs_fn rhs,
    poincare_jacobian_fn jacobian,
    const poincare_config_t* config,
    double period,
    const double* fixed_point,
    double* monodromy_out,
    void* user_data
);

#ifdef __cplusplus
}
#endif

#endif /* POINCARE_SEC_H */
