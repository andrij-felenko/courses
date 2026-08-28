#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define EMPTY -2000000000

/* Швидкий генератор випадкових чисел xorshift64 */
static uint64_t rng_state = 88172645463325252ULL;

static inline uint32_t fast_rand(void) {
    rng_state ^= rng_state << 13;
    rng_state ^= rng_state >> 7;
    rng_state ^= rng_state << 17;
    return (uint32_t)(rng_state & 0xFFFFFFFF);
}

typedef struct {
    int L;
    int N;
    int *parent;     /* parent[i] >= 0: батько; parent[i] < 0: -розмір кореня */
    uint8_t *mask;   /* бітова маска меж для кожного вузла/кореня */
    int *order;      /* випадкова перестановка індексів сайтів */
    int *s_max;      /* мікроканонічний розмір макс. кластера для кожного кроку n */
    bool percolated;
    int perc_step;   /* крок n, на якому виникло перше наскрізне протікання */
} NZSimulation;

NZSimulation* nz_create(int L) {
    NZSimulation *sim = (NZSimulation*)malloc(sizeof(NZSimulation));
    if (!sim) return NULL;

    sim->L = L;
    sim->N = L * L;
    sim->parent = (int*)malloc(sizeof(int) * sim->N);
    sim->mask = (uint8_t*)malloc(sizeof(uint8_t) * sim->N);
    sim->order = (int*)malloc(sizeof(int) * sim->N);
    sim->s_max = (int*)malloc(sizeof(int) * (sim->N + 1));
    sim->percolated = false;
    sim->perc_step = -1;

    for (int i = 0; i < sim->N; i++) {
        sim->parent[i] = EMPTY;
        sim->mask[i] = 0;
        sim->order[i] = i;
    }
    sim->s_max[0] = 0;

    /* Перемішування Кнута (Fisher-Yates shuffle) */
    for (int i = sim->N - 1; i > 0; i--) {
        int j = fast_rand() % (i + 1);
        int tmp = sim->order[i];
        sim->order[i] = sim->order[j];
        sim->order[j] = tmp;
    }

    return sim;
}

void nz_destroy(NZSimulation *sim) {
    if (!sim) return;
    free(sim->parent);
    free(sim->mask);
    free(sim->order);
    free(sim->s_max);
    free(sim);
}

int nz_find(NZSimulation *sim, int i) {
    if (sim->parent[i] < 0) return i;
    return sim->parent[i] = nz_find(sim, sim->parent[i]);
}

int nz_union(NZSimulation *sim, int r1, int r2) {
    if (r1 == r2) return r1;

    /* r1 робимо коренем більшого за розміром дерева */
    if (sim->parent[r1] > sim->parent[r2]) {
        int tmp = r1;
        r1 = r2;
        r2 = tmp;
    }

    /* Додаємо розмір r2 до r1 (значення від'ємні) */
    sim->parent[r1] += sim->parent[r2];
    sim->parent[r2] = r1;
    sim->mask[r1] |= sim->mask[r2];

    /* Перевірка вертикального протікання: верх (0x01) і низ (0x02) */
    if (!sim->percolated && (sim->mask[r1] & 0x03) == 0x03) {
        sim->percolated = true;
    }

    return r1;
}

void nz_run(NZSimulation *sim) {
    int max_cluster = 0;
    int L = sim->L;

    for (int step = 1; step <= sim->N; step++) {
        int site = sim->order[step - 1];
        int x = site % L;
        int y = site / L;

        /* Ініціалізація нового вузла як одномісного кластера розміром 1 */
        sim->parent[site] = -1;
        uint8_t m = 0;
        if (y == 0)     m |= 0x01;  /* верхня межа */
        if (y == L - 1) m |= 0x02;  /* нижня межа */
        if (x == 0)     m |= 0x04;  /* ліва межа */
        if (x == L - 1) m |= 0x08;  /* права межа */
        sim->mask[site] = m;

        int root = site;
        if (max_cluster < 1) max_cluster = 1;

        /* Опитування 4 ортогональних сусідів */
        int dx[4] = {0, 0, -1, 1};
        int dy[4] = {-1, 1, 0, 0};

        for (int k = 0; k < 4; k++) {
            int nx = x + dx[k];
            int ny = y + dy[k];

            if (nx >= 0 && nx < L && ny >= 0 && ny < L) {
                int n_idx = ny * L + nx;
                if (sim->parent[n_idx] != EMPTY) {
                    int n_root = nz_find(sim, n_idx);
                    if (n_root != root) {
                        root = nz_union(sim, root, n_root);
                    }
                }
            }
        }

        int cur_size = -sim->parent[root];
        if (cur_size > max_cluster) {
            max_cluster = cur_size;
        }

        sim->s_max[step] = max_cluster;

        if (sim->percolated && sim->perc_step == -1) {
            sim->perc_step = step;
        }
    }
}

/* Біноміальна згортка для обчислення середнього розміру P_infinity(p) */
double nz_canonical_p_inf(const NZSimulation *sim, double p) {
    int N = sim->N;
    double log_p = log(p);
    double log_1_p = log(1.0 - p);

    /* Знаходження моди розподілу для числової стабільності */
    int n_mode = (int)(N * p);
    if (n_mode < 0) n_mode = 0;
    if (n_mode > N) n_mode = N;

    /* Обчислення логарифма ваги моди */
    double log_weight_mode = 0.0;
    for (int i = 1; i <= n_mode; i++) {
        log_weight_mode += log((double)(N - i + 1) / (double)i);
    }
    log_weight_mode += n_mode * log_p + (N - n_mode) * log_1_p;

    /* Інтегрування у вікні ±5 стандартних відхилень навколо моди */
    double sigma = sqrt(N * p * (1.0 - p));
    int n_min = (int)(n_mode - 6.0 * sigma);
    int n_max = (int)(n_mode + 6.0 * sigma);
    if (n_min < 0) n_min = 0;
    if (n_max > N) n_max = N;

    double weighted_sum = 0.0;
    double norm = 0.0;

    for (int n = n_min; n <= n_max; n++) {
        double log_c = 0.0;
        int k_min = (n < N - n) ? n : N - n;
        for (int i = 1; i <= k_min; i++) {
            log_c += log((double)(N - i + 1) / (double)i);
        }
        double log_w = log_c + n * log_p + (N - n) * log_1_p - log_weight_mode;
        double w = exp(log_w);

        weighted_sum += (double)sim->s_max[n] * w;
        norm += w;
    }

    if (norm == 0.0) return 0.0;
    return (weighted_sum / norm) / (double)N;
}
