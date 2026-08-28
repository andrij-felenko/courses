#ifndef SIMULATED_ANNEALING_H
#define SIMULATED_ANNEALING_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Швидкий генератор псевдовипадкових чисел xoshiro256** */
typedef struct {
    uint64_t s[4];
} sa_rng_t;

void sa_rng_seed(sa_rng_t* rng, uint64_t seed);
uint64_t sa_rng_next64(sa_rng_t* rng);
double sa_rng_uniform(sa_rng_t* rng); /* Повертає значення у діапазоні [0.0, 1.0) */

/* Типи температурних розкладів */
typedef enum {
    SA_COOLING_GEOMETRIC,   /* T_{k+1} = alpha * T_k */
    SA_COOLING_LINEAR,      /* T_{k+1} = max(T_min, T_k - beta) */
    SA_COOLING_LOGARITHMIC  /* T_k = T_0 / ln(1 + k) */
} sa_cooling_type_t;

/* Параметри конфігурації оптимізатора */
typedef struct {
    double initial_temp;     /* T_0: початкова температура */
    double min_temp;         /* T_min: температура зупинки */
    double cooling_rate;     /* alpha (0.80..0.99) для GEOMETRIC або beta для LINEAR */
    size_t steps_per_epoch;  /* Кількість кроків на кожному ізотермічному рівні */
    size_t max_epochs;       /* Максимальна кількість епох охолодження */
    size_t max_stagnation;   /* Ліміт епох без оновлення глобального рекорду */
    size_t resync_interval;  /* Інтервал повної ресинхронізації енергії (ітерацій) */
    sa_cooling_type_t type;  /* Обраний температурний розклад */
} sa_params_t;

/* Статистика та метрики виконання */
typedef struct {
    uint64_t total_proposals;
    uint64_t accepted_improvements;
    uint64_t accepted_deteriorations;
    uint64_t rejected_moves;
    double best_energy;
    double final_temp;
    size_t epochs_run;
} sa_stats_t;

/* Контракт проблемно-орієнтованої моделі */
typedef struct sa_problem {
    void* context; /* Користувацькі дані задачі (матриці ваг, координати тощо) */
    
    /* Повний розрахунок вартості початкового стану O(N) */
    double (*evaluate_full)(const void* state, void* context);
    
    /* Генерація випадкової мутації з околу N(state) */
    void (*propose_move)(const void* state, void* move_out, sa_rng_t* rng, void* context);
    
    /* Інкрементний розрахунок різниці енергії: ΔE = E(state') - E(state) за O(1) */
    double (*evaluate_delta)(const void* state, const void* move, void* context);
    
    /* Застосування прийнятої мутації до стану на місці */
    void (*apply_move)(void* state, const void* move, void* context);
    
    /* Копіювання стану для збереження глобального рекорду */
    void (*copy_state)(void* dst, const void* src, void* context);
    
    /* Опціональний зворотний виклик для телеметрії (може бути NULL) */
    void (*on_epoch_end)(size_t epoch, double temp, double best_energy, 
                         double acceptance_rate, void* context);
} sa_problem_t;

/* Головна функція запуску оптимізатора */
bool sa_optimize(const sa_problem_t* problem,
                 void* state_io,
                 size_t state_size,
                 size_t move_size,
                 const sa_params_t* params,
                 uint64_t random_seed,
                 sa_stats_t* stats_out);

#ifdef __cplusplus
}
#endif

#endif /* SIMULATED_ANNEALING_H */
