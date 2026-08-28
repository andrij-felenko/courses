#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>
#include <time.h>
#include <string.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

/* Генератор псевдовипадкових чисел Xoshiro256** для швидкої генерації */
typedef struct {
    uint64_t s[4];
} xoshiro_state_t;

static inline uint64_t rotl(const uint64_t x, int k) {
    return (x << k) | (x >> (64 - k));
}

static uint64_t xoshiro_next(xoshiro_state_t *state) {
    const uint64_t result = rotl(state->s[1] * 5, 7) * 9;
    const uint64_t t = state->s[1] << 17;

    state->s[2] ^= state->s[0];
    state->s[3] ^= state->s[1];
    state->s[1] ^= state->s[2];
    state->s[0] ^= state->s[3];

    state->s[2] ^= t;
    state->s[3] = rotl(state->s[3], 45);

    return result;
}

static void xoshiro_seed(xoshiro_state_t *state, uint64_t seed) {
    for (int i = 0; i < 4; ++i) {
        seed = seed * 6364136223846793005ULL + 1442695040888963407ULL;
        state->s[i] = seed;
    }
}

/* Рівномірне дійсне число у діапазоні (0, 1] */
static double rand_uniform(xoshiro_state_t *state) {
    return (xoshiro_next(state) >> 11) * (1.0 / 9007199254740992.0) + 1e-15;
}

/* Генерація стандартного нормального числа за методом Бокса — Мюллера */
static float rand_gaussian(xoshiro_state_t *state) {
    double u1 = rand_uniform(state);
    double u2 = rand_uniform(state);
    return (float)(sqrt(-2.0 * log(u1)) * cos(2.0 * M_PI * u2));
}

/* Типи матриць проєктування */
typedef enum {
    PROJECTION_GAUSSIAN,
    PROJECTION_SPARSE_ACHLIOPTAS
} projection_type_t;

typedef struct {
    int orig_dim;       /* d */
    int target_dim;     /* k */
    projection_type_t type;
    float *matrix;      /* плоский масив k * d */
} random_projector_t;

/* Створення та ініціалізація проєктора */
random_projector_t *projector_create(int orig_dim, int target_dim, projection_type_t type, uint64_t seed) {
    random_projector_t *proj = (random_projector_t *)malloc(sizeof(random_projector_t));
    if (!proj) return NULL;

    proj->orig_dim = orig_dim;
    proj->target_dim = target_dim;
    proj->type = type;
    proj->matrix = (float *)malloc((size_t)orig_dim * (size_t)target_dim * sizeof(float));
    if (!proj->matrix) {
        free(proj);
        return NULL;
    }

    xoshiro_state_t rng;
    xoshiro_seed(&rng, seed);

    float scale = 1.0f / sqrtf((float)target_dim);

    if (type == PROJECTION_GAUSSIAN) {
        for (int i = 0; i < target_dim * orig_dim; ++i) {
            proj->matrix[i] = rand_gaussian(&rng) * scale;
        }
    } else if (type == PROJECTION_SPARSE_ACHLIOPTAS) {
        /* Значення: +√3 з імовірністю 1/6, -√3 з імовірністю 1/6, 0 з імовірністю 2/3 */
        float val = sqrtf(3.0f) * scale;
        for (int i = 0; i < target_dim * orig_dim; ++i) {
            double r = rand_uniform(&rng);
            if (r < 1.0 / 6.0) {
                proj->matrix[i] = val;
            } else if (r < 2.0 / 6.0) {
                proj->matrix[i] = -val;
            } else {
                proj->matrix[i] = 0.0f;
            }
        }
    }

    return proj;
}

void projector_free(random_projector_t *proj) {
    if (proj) {
        free(proj->matrix);
        free(proj);
    }
}

/* Проєктування одного вектора: out = (1/√k) * R * in */
void projector_transform(const random_projector_t *proj, const float *in_vec, float *out_vec) {
    int k = proj->target_dim;
    int d = proj->orig_dim;

    for (int i = 0; i < k; ++i) {
        const float *row = &proj->matrix[i * d];
        float sum = 0.0f;
        for (int j = 0; j < d; ++j) {
            sum += row[j] * in_vec[j];
        }
        out_vec[i] = sum;
    }
}

/* Евклідова відстань між двома векторами */
static float euclidean_distance(const float *a, const float *b, int dim) {
    float sum = 0.0f;
    for (int i = 0; i < dim; ++i) {
        float diff = a[i] - b[i];
        sum += diff * diff;
    }
    return sqrtf(sum);
}

int main(void) {
    const int N = 300;         /* Кількість точок */
    const int D = 2048;        /* Початкова розмірність */
    const int K = 128;         /* Цільова розмірність */
    const float EPS = 0.20f;   /* Допустима похибка 20% */

    printf("=== Бенчмарк випадкового проєктування (C) ===\n");
    printf("Точок: %d, Початкова розмірність d: %d, Цільова k: %d\n\n", N, D, K);

    /* 1. Генерація випадкових даних */
    float *original_data = (float *)malloc((size_t)N * D * sizeof(float));
    float *projected_data = (float *)malloc((size_t)N * K * sizeof(float));

    xoshiro_state_t data_rng;
    xoshiro_seed(&data_rng, 987654321ULL);

    for (int i = 0; i < N * D; ++i) {
        original_data[i] = rand_gaussian(&data_rng);
    }

    /* 2. Створення розрідженого проєктора Ахіоптаса */
    random_projector_t *proj = projector_create(D, K, PROJECTION_SPARSE_ACHLIOPTAS, 42ULL);
    if (!proj) {
        fprintf(stderr, "Помилка виділення пам'яті під проєктор\n");
        return 1;
    }

    /* 3. Проєктування всіх векторів */
    clock_t t_proj_start = clock();
    for (int i = 0; i < N; ++i) {
        projector_transform(proj, &original_data[i * D], &projected_data[i * K]);
    }
    clock_t t_proj_end = clock();
    double proj_ms = 1000.0 * (double)(t_proj_end - t_proj_start) / CLOCKS_PER_SEC;
    printf("Час проєктування %d векторів: %.2f мс (%.3f мкс/вектор)\n\n", N, proj_ms, (proj_ms * 1000.0) / N);

    /* 4. Перевірка попарних відстаней та спотворення */
    int total_pairs = N * (N - 1) / 2;
    int within_eps_count = 0;
    float max_distortion = 0.0f;
    double sum_distortion = 0.0;

    for (int i = 0; i < N; ++i) {
        for (int j = i + 1; j < N; ++j) {
            float dist_orig = euclidean_distance(&original_data[i * D], &original_data[j * D], D);
            float dist_proj = euclidean_distance(&projected_data[i * K], &projected_data[j * K], K);

            float ratio = dist_proj / dist_orig;
            float distortion = fabsf(ratio - 1.0f);

            if (distortion > max_distortion) max_distortion = distortion;
            sum_distortion += distortion;

            if (fabsf(ratio * ratio - 1.0f) <= EPS) {
                within_eps_count++;
            }
        }
    }

    float mean_distortion = (float)(sum_distortion / total_pairs);
    float success_rate = 100.0f * (float)within_eps_count / (float)total_pairs;

    printf("--- Результати перевірки леми Джонсона — Лінденштрауса ---\n");
    printf("Всього попарних відстаней: %d\n", total_pairs);
    printf("Середнє відносне спотворення відстані: %.2f%%\n", mean_distortion * 100.0f);
    printf("Максимальне відносне спотворення:      %.2f%%\n", max_distortion * 100.0f);
    printf("Пар у межах заданої похибки (ε = %.2f): %.2f%% (%d / %d)\n",
           EPS, success_rate, within_eps_count, total_pairs);

    projector_free(proj);
    free(original_data);
    free(projected_data);
    return 0;
}
