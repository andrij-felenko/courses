#include <stdlib.h>

/* Обчислення суми вікна j за алгоритмом Піппенджера */
void compute_window_sum(
    point_jacobian_t *window_sum,
    const point_affine_t *points,
    const fe256_t *scalars,
    size_t n,
    uint32_t window_idx,
    uint32_t c
) {
    uint32_t num_buckets = (1U << c) - 1U;
    point_jacobian_t *buckets = (point_jacobian_t*)calloc(num_buckets, sizeof(point_jacobian_t));
    if (!buckets) {
        memset(window_sum, 0, sizeof(point_jacobian_t));
        return;
    }

    /* 1. Розподіл n точок по кошиках */
    for (size_t i = 0; i < n; ++i) {
        uint32_t digit = extract_window(&scalars[i], window_idx, c);
        if (digit > 0) {
            uint32_t bucket_idx = digit - 1;
            point_add_mixed(&buckets[bucket_idx], &buckets[bucket_idx], &points[i]);
        }
    }

    /* 2. Зворотне накопичення Running Sums */
    point_jacobian_t running_sum;
    memset(&running_sum, 0, sizeof(point_jacobian_t));
    memset(window_sum, 0, sizeof(point_jacobian_t));

    for (int32_t v = (int32_t)num_buckets - 1; v >= 0; --v) {
        if (!fe256_is_zero(&buckets[v].Z)) {
            point_add_jacobian(&running_sum, &running_sum, &buckets[v]);
        }
        if (!fe256_is_zero(&running_sum.Z)) {
            point_add_jacobian(window_sum, window_sum, &running_sum);
        }
    }

    free(buckets);
}
