/* duffing_engine.h — Публічний заголовок C-бібліотеки libduffing */
#ifndef DUFFING_ENGINE_H
#define DUFFING_ENGINE_H

#include <stddef.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Статуси виконання та коди помилок */
typedef enum {
    DUFFING_SUCCESS               =  0,
    DUFFING_ERROR_INVALID_PARAM   = -1,
    DUFFING_ERROR_NULL_POINTER    = -2,
    DUFFING_ERROR_NUMERICAL_DIVERGE = -3,
    DUFFING_ERROR_ALLOCATION_FAIL = -4
} duffing_status_t;

/* Конфігурація параметрів механічної системи */
typedef struct {
    double alpha;  /* лінійна жорсткість (позитивна для 1-ямного, негативна для 2-ямного) */
    double beta;   /* кубічна нелінійність (β != 0) */
    double delta;  /* коефіцієнт згасання (δ >= 0) */
    double gamma;  /* амплітуда зовнішнього збудження (γ >= 0) */
    double omega;  /* частота зовнішньої сили (ω > 0) */
} duffing_config_t;

/* Вектор фазового стану системи */
typedef struct {
    double x;      /* координата зміщення */
    double v;      /* швидкість */
    double t;      /* поточний час */
} duffing_state_t;

/* Непрозорий вказівник на обчислювальний контекст розв'язувача */
typedef struct duffing_solver duffing_solver_t;

/* Створення та ініціалізація екземпляра розв'язувача */
duffing_status_t duffing_solver_create(
    const duffing_config_t* config,
    duffing_state_t initial_state,
    double step_size,
    duffing_solver_t** out_solver
);

/* Виконання одного кроку інтегрування (RK4) */
duffing_status_t duffing_solver_step(duffing_solver_t* solver);

/* Пропуск перехідного процесу протягом вказаної кількості періодів */
duffing_status_t duffing_solver_run_transient(
    duffing_solver_t* solver,
    size_t num_periods
);

/* Заповнення масиву точками перерізу Пуанкаре (одна точка на кожен період) */
duffing_status_t duffing_solver_sample_poincare(
    duffing_solver_t* solver,
    duffing_state_t* out_points,
    size_t num_points,
    size_t steps_per_period
);

/* Зчитування поточного стану розв'язувача */
duffing_status_t duffing_solver_get_state(
    const duffing_solver_t* solver,
    duffing_state_t* out_state
);

/* Звільнення ресурсів розв'язувача */
void duffing_solver_destroy(duffing_solver_t* solver);

#ifdef __cplusplus
}
#endif

#endif /* DUFFING_ENGINE_H */
