#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>
#include <string.h>

/* Швидкий генератор псевдовипадкових чисел xoshiro256** */
typedef struct {
    uint64_t s[4];
} rng_state_t;

static inline uint64_t rotl(const uint64_t x, int k) {
    return (x << k) | (x >> (64 - k));
}

static uint64_t rng_next(rng_state_t* rng) {
    const uint64_t result = rotl(rng->s[1] * 5, 7) * 9;
    const uint64_t t = rng->s[1] << 17;
    rng->s[2] ^= rng->s[0];
    rng->s[3] ^= rng->s[1];
    rng->s[1] ^= rng->s[2];
    rng->s[0] ^= rng->s[3];
    rng->s[2] ^= t;
    rng->s[3] = rotl(rng->s[3], 45);
    return result;
}

static inline double rng_uniform(rng_state_t* rng) {
    /* Генерація числа у проміжку [0.0, 1.0) з 53-бітною точністю мантиси */
    return (rng_next(rng) >> 11) * (1.0 / 9007199254740992.0);
}

typedef struct {
    double x;
    double y;
} point_t;

typedef struct {
    size_t count;
    point_t* cities;
} tsp_instance_t;

static inline double distance_2d(point_t a, point_t b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return sqrt(dx * dx + dy * dy);
}

/* Повний розрахунок довжини маршруту за O(N) */
static double calculate_total_distance(const tsp_instance_t* inst, const size_t* tour) {
    double total = 0.0;
    for (size_t i = 0; i < inst->count; ++i) {
        size_t next = (i + 1 == inst->count) ? 0 : i + 1;
        total += distance_2d(inst->cities[tour[i]], inst->cities[tour[next]]);
    }
    return total;
}

/* Інверсія відрізка масиву міст для 2-opt */
static void apply_2opt_reverse(size_t* tour, size_t i, size_t j) {
    while (i < j) {
        size_t temp = tour[i];
        tour[i] = tour[j];
        tour[j] = temp;
        ++i;
        --j;
    }
}

typedef struct {
    double initial_temp;
    double min_temp;
    double alpha;
    size_t epoch_length;
} sa_config_t;

double solve_tsp_simulated_annealing(const tsp_instance_t* inst,
                                     size_t* best_tour_out,
                                     const sa_config_t* cfg,
                                     uint64_t seed) {
    rng_state_t rng = {{seed ^ 0x9E3779B97F4A7C15ULL, seed, seed + 1, seed + 2}};
    size_t n = inst->count;

    size_t* current_tour = (size_t*)malloc(n * sizeof(size_t));
    if (!current_tour) return -1.0;

    for (size_t i = 0; i < n; ++i) current_tour[i] = i;
    memcpy(best_tour_out, current_tour, n * sizeof(size_t));

    double current_energy = calculate_total_distance(inst, current_tour);
    double best_energy = current_energy;
    double temp = cfg->initial_temp;

    while (temp > cfg->min_temp) {
        for (size_t step = 0; step < cfg->epoch_length; ++step) {
            /* Вибір двох випадкових індексів */
            size_t idx1 = (size_t)(rng_next(&rng) % n);
            size_t idx2 = (size_t)(rng_next(&rng) % n);
            if (idx1 == idx2) continue;
            
            size_t i = (idx1 < idx2) ? idx1 : idx2;
            size_t j = (idx1 < idx2) ? idx2 : idx1;
            if (i == 0 && j == n - 1) continue; // Повний розворот туру зберігає той самий цикл

            size_t u = current_tour[i];
            size_t v = current_tour[i + 1];
            size_t w = current_tour[j];
            size_t z = current_tour[(j + 1 == n) ? 0 : j + 1];

            /* Інкрементний розрахунок різниці вартості за O(1) */
            double d_old = distance_2d(inst->cities[u], inst->cities[v]) +
                           distance_2d(inst->cities[w], inst->cities[z]);
            double d_new = distance_2d(inst->cities[u], inst->cities[w]) +
                           distance_2d(inst->cities[v], inst->cities[z]);
            double delta_e = d_new - d_old;

            bool accept = false;
            if (delta_e <= 0.0) {
                accept = true;
            } else {
                double prob = exp(-delta_e / temp);
                if (rng_uniform(&rng) < prob) {
                    accept = true;
                }
            }

            if (accept) {
                apply_2opt_reverse(current_tour, i + 1, j);
                current_energy += delta_e;

                if (current_energy < best_energy) {
                    best_energy = current_energy;
                    memcpy(best_tour_out, current_tour, n * sizeof(size_t));
                }
            }
        }
        temp *= cfg->alpha;
    }

    free(current_tour);
    return best_energy;
}
