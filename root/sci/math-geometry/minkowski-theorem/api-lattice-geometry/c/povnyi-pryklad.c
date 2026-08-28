#include <stdio.h>
#include <stdlib.h>
#include <inttypes.h>
#include "latgeom.h"

int main(void) {
    /* Базис 3-вимірної ґратки */
    const size_t dim = 3;
    const int64_t raw_matrix[9] = {
        5, 2, 1,
        0, 4, 3,
        1, 1, 6
    };

    latgeom_basis_t basis;
    latgeom_status_t status = latgeom_basis_init(&basis, dim, raw_matrix);
    if (status != LATGEOM_SUCCESS) {
        fprintf(stderr, "Помилка ініціалізації: код %d\n", status);
        return EXIT_FAILURE;
    }

    status = latgeom_basis_orthogonalize(&basis);
    if (status != LATGEOM_SUCCESS) {
        fprintf(stderr, "Помилка ортогоналізації: код %d\n", status);
        latgeom_basis_free(&basis);
        return EXIT_FAILURE;
    }

    printf("=== Інформація про ґратку (liblatgeom) ===\n");
    printf("Розмірність: %zu\n", basis.dim);
    printf("Визначник det(L): %.4f\n", basis.determinant);
    printf("Логарифм визначника ln(det(L)): %.4f\n", basis.log_determinant);
    printf("Дефект ортогональності: %.4f\n", basis.orthogonality_defect);
    printf("Радіус кулі Мінковського R_M: %.4f\n", basis.minkowski_radius);
    printf("Гауссова евристика GH(L): %.4f\n", basis.gaussian_heuristic);

    /* Створення кулі Мінковського для перевірки умови */
    latgeom_convex_body_t ball;
    ball.dim = dim;
    ball.type = LATGEOM_BODY_ELLIPSOID;
    ball.radius = basis.minkowski_radius;
    ball.volume = (4.0 / 3.0) * 3.141592653589793 * basis.minkowski_radius * basis.minkowski_radius * basis.minkowski_radius;

    bool guaranteed = false;
    double ratio = 0.0;
    latgeom_minkowski_check(&basis, &ball, &guaranteed, &ratio);
    printf("Співвідношення об'ємів vol(K) / (2^n * det(L)): %.4f\n", ratio);
    printf("Наявність вузла гарантована теоремою: %s\n", guaranteed ? "ТАК" : "НІ");

    /* Пошук найкоротшого вектора SVP */
    latgeom_svp_result_t svp_res;
    svp_res.coordinates = (int64_t*)malloc(dim * sizeof(int64_t));
    svp_res.vector = (double*)malloc(dim * sizeof(double));

    status = latgeom_svp_solve(&basis, 1000000ULL, &svp_res);
    if (status == LATGEOM_SUCCESS) {
        printf("\nЗнайдено найкоротший вектор v: [ ");
        for (size_t i = 0; i < dim; i++) {
            printf("%.2f ", svp_res.vector[i]);
        }
        printf("]\n");
        printf("Цілі коефіцієнти z: [ ");
        for (size_t i = 0; i < dim; i++) {
            printf("%" PRId64 " ", svp_res.coordinates[i]);
        }
        printf("]\n");
        printf("Довжина ||v|| = lambda_1(L): %.4f\n", svp_res.euclidean_norm);
        printf("Фактор Ерміта: %.4f\n", svp_res.hermite_factor);
        printf("Перевірка теореми: %.4f <= %.4f (%s)\n",
               svp_res.euclidean_norm, basis.minkowski_radius,
               svp_res.euclidean_norm <= basis.minkowski_radius ? "УСПІХ" : "ПОРУШЕННЯ");
        printf("Відвідано вузлів: %" PRIu64 "\n", svp_res.visited_nodes);
    } else {
        fprintf(stderr, "Помилка під час пошуку SVP: код %d\n", status);
    }

    free(svp_res.coordinates);
    free(svp_res.vector);
    latgeom_basis_free(&basis);
    return EXIT_SUCCESS;
}
