#include "floquet_solver.h"
#include <stdio.h>
#include <math.h>

/* Система Матьє у C-стилі */
static void mathieu_rhs(double t, size_t n, double* out_matrix, void* user_data) {
    (void)user_data;
    double a = 1.5;
    double q = 0.2;
    double f_t = a - 2.0 * q * cos(2.0 * t);

    out_matrix[0 * n + 0] = 0.0;
    out_matrix[0 * n + 1] = 1.0;
    out_matrix[1 * n + 0] = -f_t;
    out_matrix[1 * n + 1] = 0.0;
}

int main(void) {
    floquet_config_t config = {
        .dim = 2,
        .period = 3.141592653589793,
        .steps = 1000,
        .tol = 1e-5
    };

    floquet_result_t result;
    if (floquet_result_alloc(config.dim, &result) != FLOQUET_SUCCESS) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return 1;
    }

    floquet_status_t status = floquet_solve(&config, mathieu_rhs, NULL, &result);
    if (status == FLOQUET_SUCCESS) {
        printf("Обчислення успішне!\n");
        printf("Слід M: %.6f\n", result.trace);
        printf("Максимальний модуль |lambda|: %.6f\n", result.max_modulus);
        printf("Система стійка: %s\n", result.is_stable ? "ТАК" : "НІ");
    } else {
        fprintf(stderr, "Помилка обчислення: %d\n", status);
    }

    floquet_result_free(&result);
    return 0;
}
