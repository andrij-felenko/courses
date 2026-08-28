#define _POSIX_C_SOURCE 199309L
#include <stdio.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>
#include <unistd.h>

#define PLANNING_BUDGET_US   40000ULL /* Бюджет кванту часу: 40 мс (40000 мкс) */
#define SAFETY_MARGIN_US      4000ULL /* Резерв на відправку та валідацію: 4 мс */

typedef struct {
    double x, y, z;
} Point3D;

typedef struct {
    Point3D waypoints[16];
    size_t count;
    double cost;
    uint32_t iteration;
    bool is_valid;
} TrajectoryPlan;

static inline uint64_t get_monotonic_us(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
    return (uint64_t)ts.tv_sec * 1000000ULL + (uint64_t)ts.tv_nsec / 1000ULL;
}

/* Імітація ітеративного покращення траєкторії */
bool optimize_trajectory_step(TrajectoryPlan* plan, uint32_t step, uint64_t deadline_us) {
    /* Симуляція обчислень: перевірка часу перед кожною важкою операцією */
    if (get_monotonic_us() >= deadline_us) {
        return false; /* Дедлайн вичерпано — припиняємо роботу */
    }
    
    /* Ітеративне покращення кривої */
    plan->iteration = step;
    plan->cost *= 0.85; /* Зниження ривка / покращення плавності */
    plan->is_valid = true;
    
    /* Симуляція навантаження 1.5 мс */
    usleep(1500);
    return true;
}

/* Головний цикл планування з жорстким часовим дедлайном */
TrajectoryPlan execute_planning_cycle(const TrajectoryPlan* fallback_plan) {
    uint64_t start_time_us = get_monotonic_us();
    uint64_t deadline_us = start_time_us + (PLANNING_BUDGET_US - SAFETY_MARGIN_US);
    
    TrajectoryPlan current_best;
    if (fallback_plan && fallback_plan->is_valid) {
        current_best = *fallback_plan; /* Ініціалізація гарантованим резервним планом */
    } else {
        current_best.count = 1;
        current_best.cost = 99999.0;
        current_best.iteration = 0;
        current_best.is_valid = false;
    }
    
    uint32_t step = 1;
    while (get_monotonic_us() < deadline_us) {
        TrajectoryPlan candidate = current_best;
        if (!optimize_trajectory_step(&candidate, step, deadline_us)) {
            break; /* Оптимізація була перервана таймером */
        }
        current_best = candidate;
        step++;
    }
    
    uint64_t total_elapsed_us = get_monotonic_us() - start_time_us;
    printf("[Anytime C] Цикл завершено за %llu мкс (Ітерацій: %u, Вартість: %.2f)\n",
           (unsigned long long)total_elapsed_us, current_best.iteration, current_best.cost);
    
    return current_best;
}
