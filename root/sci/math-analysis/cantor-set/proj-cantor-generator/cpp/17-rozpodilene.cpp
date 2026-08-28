#include <mpi.h>
#include <vector>
#include <execution>

void distributed_cantor_scan_cpp(std::span<const double> points, std::vector<uint8_t>& results) {
    results.resize(points.size());
    std::transform(std::execution::par_unseq, points.begin(), points.end(), results.begin(), [](double pt) {
        return math::fractals::CantorGenerator::contains_point(pt, 30) ? 1 : 0;
    });
    MPI_Barrier(MPI_COMM_WORLD);
}
