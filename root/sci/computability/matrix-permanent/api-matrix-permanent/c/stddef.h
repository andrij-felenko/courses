#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Обчислення перманента цілочисельної 64-бітної матриці n x n.
 *
 * @param[in]  matrix   Вказівник на плоский масив елементів розміром n*n в C-style (row-major).
 * @param[in]  n        Розмірність квадратної матриці (n <= 62).
 * @param[in]  cfg      Вказівник на конфігурацію (можна NULL для параметрів за замовчуванням).
 * @param[out] out_perm Вказівник на змінну для запису результату.
 * @return Код статусу perm_status_t.
 */
perm_status_t perm_compute_u64(const uint64_t *matrix,
                               size_t           n,
                               const perm_config_t *cfg,
                               uint64_t        *out_perm);

/**
 * @brief Обчислення перманента матриці дійсних чисел double n x n.
 *
 * @param[in]  matrix   Вказівник на плоский масив елементів n*n.
 * @param[in]  n        Розмірність квадратної матриці.
 * @param[in]  cfg      Вказівник на конфігурацію.
 * @param[out] out_perm Вказівник на змінну результату.
 * @return Код статусу perm_status_t.
 */
perm_status_t perm_compute_f64(const double    *matrix,
                               size_t           n,
                               const perm_config_t *cfg,
                               double          *out_perm);

/**
 * @brief Обчислення перманента 0/1 матриці за модулем p.
 *
 * @param[in]  matrix   Вказівник на 0/1 матрицю.
 * @param[in]  n        Розмірність матриці.
 * @param[in]  mod_p    Просте число p для модульної арифметики.
 * @param[out] out_perm Вказівник на результат mod p.
 * @return Код статусу perm_status_t.
 */
perm_status_t perm_compute_mod_p(const uint8_t *matrix,
                                 size_t          n,
                                 uint64_t        mod_p,
                                 uint64_t       *out_perm);

#ifdef __cplusplus
}
#endif
