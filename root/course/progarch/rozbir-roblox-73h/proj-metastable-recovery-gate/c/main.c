#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>
#include <time.h>
#include <pthread.h>

typedef struct {
    double base_sec;
    double max_sec;
    unsigned int seed;
    pthread_mutex_t lock;
} backoff_t;

void backoff_init(backoff_t *b, double base_sec, double max_sec) {
    b->base_sec = base_sec;
    b->max_sec = max_sec;
    b->seed = (unsigned int)time(NULL);
    pthread_mutex_init(&b->lock, NULL);
}

double backoff_calculate_sec(backoff_t *b, int attempt) {
    pthread_mutex_lock(&b->lock);
    double temp = b->base_sec * pow(2.0, (double)attempt);
    if (temp > b->max_sec) {
        temp = b->max_sec;
    }
    double r = (double)rand_r(&b->seed) / (double)RAND_MAX;
    double sleep_sec = r * temp;
    pthread_mutex_unlock(&b->lock);
    return sleep_sec;
}

typedef struct {
    double rate;       // токенів/сек
    double capacity;   // максимальна ємність
    double tokens;
    struct timespec last_update;
    pthread_mutex_t lock;
} admission_gate_t;

void admission_gate_init(admission_gate_t *g, double rate, double capacity) {
    g->rate = rate;
    g->capacity = capacity;
    g->tokens = capacity;
    clock_gettime(CLOCK_MONOTONIC, &g->last_update);
    pthread_mutex_init(&g->lock, NULL);
}

bool admission_gate_allow(admission_gate_t *g) {
    pthread_mutex_lock(&g->lock);
    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    double elapsed = (now.tv_sec - g->last_update.tv_sec) +
                     (now.tv_nsec - g->last_update.tv_nsec) / 1e9;
    g->last_update = now;

    g->tokens += elapsed * g->rate;
    if (g->tokens > g->capacity) {
        g->tokens = g->capacity;
    }

    bool allowed = false;
    if (g->tokens >= 1.0) {
        g->tokens -= 1.0;
        allowed = true;
    }
    pthread_mutex_unlock(&g->lock);
    return allowed;
}

int main(void) {
    backoff_t b;
    backoff_init(&b, 0.1, 10.0);

    printf("--- (C) Розрахунок інтервалів Backoff ---\n");
    for (int i = 0; i < 5; i++) {
        double delay = backoff_calculate_sec(&b, i);
        printf("Спроба %d: затримка %.3f сек\n", i, delay);
    }

    admission_gate_t gate;
    admission_gate_init(&gate, 50.0, 100.0);

    int allowed = 0, rejected = 0;
    for (int i = 0; i < 120; i++) {
        if (admission_gate_allow(&gate)) {
            allowed++;
        } else {
            rejected++;
        }
    }
    printf("Дозволено: %d, Відхилено: %d\n", allowed, rejected);

    pthread_mutex_destroy(&b.lock);
    pthread_mutex_destroy(&gate.lock);
    return 0;
}
