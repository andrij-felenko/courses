#ifndef POLARIZATION_LIB_H
#define POLARIZATION_LIB_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Типи даних */
typedef struct {
    double real;
    double imag;
} pol_complex_t;

typedef struct {
    pol_complex_t ex;
    pol_complex_t ey;
} pol_jones_vector_t;

typedef struct {
    pol_complex_t m[2][2];
} pol_jones_matrix_t;

typedef struct {
    double s0;
    double s1;
    double s2;
    double s3;
} pol_stokes_vector_t;

typedef struct {
    double m[4][4];
} pol_mueller_matrix_t;

/* --- Конструктори та стандартизовані генератори векторів Джонса --- */

/**
 * @brief Створює нормований вектор Джонса лінійної поляризації.
 * @param angle_rad Кут нахилу електричного поля до осі X у радіанах.
 * @param out_v Вказівник на вихідну структуру.
 * @return POL_SUCCESS або код помилки.
 */
int pol_jones_create_linear(double angle_rad, pol_jones_vector_t *out_v);

/**
 * @brief Створює нормований вектор Джонса колової поляризації.
 * @param is_right_circular true для правої (RCP), false для лівої (LCP).
 * @param out_v Вказівник на вихідну структуру.
 */
int pol_jones_create_circular(bool is_right_circular, pol_jones_vector_t *out_v);

/* --- Конструктори та генератори матриць Джонса --- */

/**
 * @brief Генератор матриці ідеального лінійного поляризатора.
 * @param angle_rad Кут осі пропускання поляризатора в радіанах.
 * @param out_m Вказівник на вихідну матрицю.
 */
int pol_jones_matrix_polarizer(double angle_rad, pol_jones_matrix_t *out_m);

/**
 * @brief Генератор матриці фазової платівки (retarder).
 * @param fast_axis_rad Кут швидкої осі платівки в радіанах.
 * @param retardance_rad Фазове запізнення в радіанах (pi/2 для QWP, pi для HWP).
 * @param out_m Вказівник на вихідну матрицю.
 */
int pol_jones_matrix_retarder(double fast_axis_rad, double retardance_rad, pol_jones_matrix_t *out_m);

/**
 * @brief Генератор матриці ротатора Фарадея або оптично активного середовища.
 * @param rotation_angle_rad Кут повороту плоскості поляризації в радіанах.
 * @param out_m Вказівник на вихідну матрицю.
 */
int pol_jones_matrix_rotator(double rotation_angle_rad, pol_jones_matrix_t *out_m);

/* --- Операції числення Джонса --- */

/**
 * @brief Застосування матриці Джонса до вектора: J_out = M * J_in.
 */
int pol_jones_apply(const pol_jones_matrix_t *m, const pol_jones_vector_t *in_v, pol_jones_vector_t *out_v);

/**
 * @brief Множення двох матриць Джонса: M_out = A * B.
 */
int pol_jones_matrix_multiply(const pol_jones_matrix_t *a, const pol_jones_matrix_t *b, pol_jones_matrix_t *out_m);

/* --- Конструктори та генератори матриць Мюллера --- */

/**
 * @brief Генератор матриці Мюллера для ідеального лінійного поляризатора.
 */
int pol_mueller_matrix_polarizer(double angle_rad, pol_mueller_matrix_t *out_m);

/**
 * @brief Генератор матриці Мюллера для фазової платівки.
 */
int pol_mueller_matrix_retarder(double fast_axis_rad, double retardance_rad, pol_mueller_matrix_t *out_m);

/**
 * @brief Генератор матриці ідеального ізотропного деполяризатора.
 * @param depol_factor Коефіцієнт деполяризації (0.0 — без деполяризації, 1.0 — повна деполяризація).
 * @param out_m Вказівник на вихідну матрицю.
 */
int pol_mueller_matrix_depolarizer(double depol_factor, pol_mueller_matrix_t *out_m);

/* --- Операції числення Мюллера --- */

/**
 * @brief Застосування матриці Мюллера до вектора Стокса: S_out = M * S_in.
 */
int pol_mueller_apply(const pol_mueller_matrix_t *m, const pol_stokes_vector_t *in_s, pol_stokes_vector_t *out_s);

/**
 * @brief Множення двох матриць Мюллера: M_out = A * B.
 */
int pol_mueller_matrix_multiply(const pol_mueller_matrix_t *a, const pol_mueller_matrix_t *b, pol_mueller_matrix_t *out_m);

/* --- Функції взаємної конверсії та аналізу станів --- */

/**
 * @brief Перетворення вектора Джонса у вектор Стокса.
 */
int pol_jones_to_stokes(const pol_jones_vector_t *in_j, pol_stokes_vector_t *out_s);

/**
 * @brief Обчислення матриці Мюллера з матриці Джонса (для недополяризуючих систем).
 */
int pol_jones_to_mueller_matrix(const pol_jones_matrix_t *in_j, pol_mueller_matrix_t *out_m);

/**
 * @brief Обчислення ступеня поляризації (DOP) вектора Стокса.
 * @param in_s Вказівник на вектор Стокса.
 * @param out_dop Вказівник на результат (0.0 <= DOP <= 1.0).
 */
int pol_stokes_get_dop(const pol_stokes_vector_t *in_s, double *out_dop);

/**
 * @brief Обчислення азимутального кута psi та кута еліптичності chi вектора Стокса.
 */
int pol_stokes_get_ellipse_params(const pol_stokes_vector_t *in_s, double *out_psi_rad, double *out_chi_rad);

/**
 * @brief Перевірка фізичної реалізованості матриці Мюллера за декомпозицією Клода.
 * @return POL_SUCCESS якщо матриця фізична, POL_ERROR_NON_PHYSICAL_MATRIX у разі порушення.
 */
int pol_mueller_check_physicality(const pol_mueller_matrix_t *m, bool *is_physical);

#ifdef __cplusplus
}
#endif

#endif /* POLARIZATION_LIB_H */
