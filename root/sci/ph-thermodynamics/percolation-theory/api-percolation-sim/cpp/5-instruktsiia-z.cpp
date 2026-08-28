#include <iostream>
#include <iomanip>
#include "percolate/percolation_engine.hpp"

int main() {
    using namespace percolate;

    PercolationConfig config;
    config.dim_x = 500;
    config.dim_y = 500;
    config.topology = LatticeTopology::SQUARE_2D;
    config.mode = PercolationMode::SITE_PERCOLATION;
    config.boundary = BoundaryCondition::PERIODIC_BOUNDARIES;

    PercolationEngine engine(config);

    std::cout << std::fixed << std::setprecision(5);
    std::cout << "p\t\tP_inf\t\tchi\t\tSpanning\n";

    for (double p = 0.50; p <= 0.70; p += 0.02) {
        if (engine.generate_lattice(p) != PercolationStatus::PERC_SUCCESS) {
            std::cerr << "Помилка генерації ґратки для p = " << p << std::endl;
            continue;
        }
        
        ClusterAnalysisResult result;
        PercolationStatus status = engine.analyze(result);
        if (status == PercolationStatus::PERC_SUCCESS) {
            std::cout << p << "\t" 
                      << result.p_infinite << "\t" 
                      << result.mean_cluster_size_chi << "\t" 
                      << (result.has_spanning_x ? "YES" : "NO") << "\n";
        } else {
            std::cerr << "Помилка аналізу кластерів: " << static_cast<int>(status) << std::endl;
        }
    }

    return 0;
}
