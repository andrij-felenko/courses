#ifndef LIBTHERMO_PHASE_H
#define LIBTHERMO_PHASE_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    THERMO_SUCCESS = 0,
    THERMO_WARN_OVERDETERMINED = 1,
    THERMO_WARN_CRITICAL_POINT = 2,
    THERMO_ERR_INVALID_SPECIES = -1,
    THERMO_ERR_INVALID_PHASES = -2,
    THERMO_ERR_NULL_POINTER = -3
} ThermoStatusCodeC;

typedef struct {
    size_t num_species;
    size_t num_reactions;
    size_t num_constraints;
    size_t num_phases;
    bool is_condensed;
    const double* stoich_matrix_flat;
} PhaseSystemSpecC;

typedef struct {
    size_t rank_reactions;
    size_t gibbs_components;
    int degrees_of_freedom;
    ThermoStatusCodeC status_code;
    const char* status_message;
} PhaseResultSpecC;

/**
 * @brief Обчислює ранг стехіометричної матриці методом Гаусса.
 * @param matrix_flat Одновимірний масив матриці розміром (rows x cols).
 * @param rows Кількість рядків (реакцій).
 * @param cols Кількість стовпчиків (сполук).
 * @param eps Поріг порівняння з нулем.
 * @return Ранг матриці або -1 при некоректних аргументах.
 */
int thermo_compute_stoich_rank(
    const double* matrix_flat,
    size_t rows,
    size_t cols,
    double eps
);

/**
 * @brief Обчислює число компонентів Гіббса K = N - R - q.
 * @param num_species Кількість речовин N.
 * @param rank_reactions Ранг стехіометричної матриці R.
 * @param num_constraints Число додаткових обмежень q.
 * @return Кількість компонентів Гіббса.
 */
size_t thermo_compute_gibbs_components(
    size_t num_species,
    size_t rank_reactions,
    size_t num_constraints
);

/**
 * @brief Обчислює варіантність гетерогенної системи F = K - P + env.
 * @param gibbs_components Число компонентів K.
 * @param num_phases Число фаз P.
 * @param is_condensed Прапор конденсованої системи (true: env=1, false: env=2).
 * @return Кількість ступенів вільності F.
 */
int thermo_compute_degrees_of_freedom(
    size_t gibbs_components,
    size_t num_phases,
    bool is_condensed
);

/**
 * @brief Головна функція повного аналізу гетерогенної фазової системи.
 * @param spec Вказівник на специфікацію системи.
 * @param result Вказівник на структуру результату.
 * @return Код статусу виконання ThermoStatusCodeC.
 */
ThermoStatusCodeC thermo_analyze_phase_system(
    const PhaseSystemSpecC* spec,
    PhaseResultSpecC* result
);

/**
 * @brief Повертає текстовий підпис коду статусу.
 * @param code Код помилки або попередження.
 * @return Статичний рядок із поясненням.
 */
const char* thermo_status_to_string(ThermoStatusCodeC code);

#ifdef __cplusplus
}
#endif

#endif /* LIBTHERMO_PHASE_H */
