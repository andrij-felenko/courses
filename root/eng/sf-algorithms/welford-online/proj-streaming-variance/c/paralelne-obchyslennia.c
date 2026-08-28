#include <omp.h>

welford_acc_t parallel_welford(const double *array, size_t total_size) {
    welford_acc_t global_acc;
    welford_init(&global_acc);

    #pragma omp parallel
    {
        welford_acc_t local_acc;
        welford_init(&local_acc);

        #pragma omp for nowait
        for (size_t i = 0; i < total_size; ++i) {
            welford_push(&local_acc, array[i]);
        }

        #pragma omp critical
        {
            welford_merge(&global_acc, &local_acc);
        }
    }

    return global_acc;
}
