#include <mpi.h>

void distributed_cantor_scan(double* local_points, size_t local_count, uint8_t* local_results) {
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    #pragma omp parallel for simd
    for (size_t i = 0; i < local_count; i++) {
        local_results[i] = cantor_contains_point(local_points[i], 30) ? 1 : 0;
    }

    MPI_Barrier(MPI_COMM_WORLD);
}
