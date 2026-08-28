#include <pthread.h>

typedef struct {
    point_jacobian_t result;
    const point_affine_t *points;
    const fe256_t *scalars;
    size_t n;
    uint32_t window_idx;
    uint32_t c;
} worker_arg_t;

static void* worker_thread(void *arg) {
    worker_arg_t *w = (worker_arg_t*)arg;
    compute_window_sum(&w->result, w->points, w->scalars, w->n, w->window_idx, w->c);
    return NULL;
}

/* Головна функція паралельного обчислення MSM за алгоритмом Піппенджера */
void msm_pippenger(
    point_jacobian_t *result,
    const point_affine_t *points,
    const fe256_t *scalars,
    size_t n
) {
    if (n == 0) {
        memset(result, 0, sizeof(point_jacobian_t));
        return;
    }

    /* Вибір оптимального вікна c */
    uint32_t c = 16;
    if (n < 4096) c = 10;
    else if (n < 65536) c = 13;
    else if (n < 524288) c = 15;

    uint32_t b = (256 + c - 1) / c;
    worker_arg_t *args = (worker_arg_t*)malloc(b * sizeof(worker_arg_t));
    pthread_t *threads = (pthread_t*)malloc(b * sizeof(pthread_t));

    /* Запуск паралельних потоків для кожного вікна */
    for (uint32_t j = 0; j < b; ++j) {
        args[j].points = points;
        args[j].scalars = scalars;
        args[j].n = n;
        args[j].window_idx = j;
        args[j].c = c;
        pthread_create(&threads[j], NULL, worker_thread, &args[j]);
    }

    /* Очікування завершення */
    for (uint32_t j = 0; j < b; ++j) {
        pthread_join(threads[j], NULL);
    }

    /* Міжвіконна агрегація за схемою Горнера */
    point_jacobian_t acc = args[b - 1].result;
    for (int32_t j = (int32_t)b - 2; j >= 0; --j) {
        for (uint32_t step = 0; step < c; ++step) {
            point_double_jacobian(&acc, &acc);
        }
        if (!fe256_is_zero(&args[j].result.Z)) {
            point_add_jacobian(&acc, &acc, &args[j].result);
        }
    }

    *result = acc;
    free(args);
    free(threads);
}
