#include <stdio.h>
#include <time.h>

/* Наївне послідовне обчислення MSM для перевірки коректності */
void msm_naive_reference(
    point_jacobian_t *result,
    const point_affine_t *points,
    const fe256_t *scalars,
    size_t n
) {
    memset(result, 0, sizeof(point_jacobian_t));
    for (size_t i = 0; i < n; ++i) {
        point_jacobian_t p_acc;
        memset(&p_acc, 0, sizeof(point_jacobian_t));
        for (int32_t b = 255; b >= 0; --b) {
            point_double_jacobian(&p_acc, &p_acc);
            uint32_t word = b / 64;
            uint32_t bit = b % 64;
            if ((scalars[i].d[word] >> bit) & 1U) {
                point_add_mixed(&p_acc, &p_acc, &points[i]);
            }
        }
        point_add_jacobian(result, result, &p_acc);
    }
}

/* Запуск вимірювань продуктивності */
void benchmark_msm_pipeline(size_t n) {
    point_affine_t *points = (point_affine_t*)malloc(n * sizeof(point_affine_t));
    fe256_t *scalars = (fe256_t*)malloc(n * sizeof(fe256_t));

    /* Ініціалізація тестових точок та скалярів */
    for (size_t i = 0; i < n; ++i) {
        scalars[i].d[0] = (uint64_t)i * 0xdeadbeefULL + 17;
        scalars[i].d[1] = 0x12345678ULL;
        scalars[i].d[2] = 0;
        scalars[i].d[3] = 0;
        points[i].is_infinity = false;
        fe256_set_one(&points[i].x);
        fe256_set_one(&points[i].y);
    }

    point_jacobian_t res;
    clock_t t0 = clock();
    msm_pippenger(&res, points, scalars, n);
    clock_t t1 = clock();

    double elapsed_ms = (double)(t1 - t0) * 1000.0 / CLOCKS_PER_SEC;
    (void)elapsed_ms;

    free(points);
    free(scalars);
}
