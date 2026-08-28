#ifndef MCMC_ENGINE_H
#define MCMC_ENGINE_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    MCMC_SUCCESS = 0,
    MCMC_ERROR_INVALID_PARAM = -1,
    MCMC_ERROR_OUT_OF_MEMORY = -2,
    MCMC_ERROR_NOT_CONVERGED = -3,
    MCMC_ERROR_BALANCE_VIOLATED = -4
} mcmc_status_t;

// Налаштування симулятора
typedef struct {
    size_t num_states;         // Кількість дискретних станів системи (> 1)
    double temperature;        // Термодинамічна температура (T > 0.0)
    size_t burn_in_steps;      // Кількість кроків релаксації перед збором статистики
    size_t sampling_steps;     // Кількість кроків збору даних
    unsigned int random_seed;  // Базове зерно генератора псевдовипадкових чисел
    double balance_tolerance;  // Пороговий допуск дисбалансу |J_ij| (наприклад 1e-4)
} mcmc_config_t;

// Результати аудиту детального балансу
typedef struct {
    double max_imbalance_flux; // Максимальне значення |P(i)*W(i->j) - P(j)*W(j->i)|
    size_t worst_edge_from;    // Індекс стану i найгіршого ребра
    size_t worst_edge_to;      // Індекс стану j найгіршого ребра
    double entropy_prod_rate;  // Оцінка швидкості генерації ентропії (dS/dt)
    bool is_balanced;          // Прапорець виконання умови детального балансу
} mcmc_balance_report_t;

// Непрозорий тип контексту двигуна
typedef struct mcmc_engine_s mcmc_engine_t;

// Створення та знищення контексту
mcmc_status_t mcmc_engine_create(const mcmc_config_t *config, mcmc_engine_t **engine_out);
mcmc_status_t mcmc_engine_destroy(mcmc_engine_t *engine);

// Встановлення енергій станів
mcmc_status_t mcmc_engine_set_energies(mcmc_engine_t *engine, const double *energies, size_t count);

// Виконання симуляції
mcmc_status_t mcmc_engine_run(mcmc_engine_t *engine);

// Збір результатів та перевірка балансу
mcmc_status_t mcmc_engine_get_probabilities(const mcmc_engine_t *engine, double *prob_out, size_t count);
mcmc_status_t mcmc_engine_verify_balance(const mcmc_engine_t *engine, mcmc_balance_report_t *report_out);

#ifdef __cplusplus
}
#endif

#endif // MCMC_ENGINE_H
