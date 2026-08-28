#include "libhamiltonian.hpp"
#include <iostream>

int main() {
    constexpr size_t n = 5;
    hamiltonian::Graph g(n);

    g.add_edge(0, 1);
    g.add_edge(1, 2);
    g.add_edge(2, 3);
    g.add_edge(3, 4);
    g.add_edge(4, 0);
    g.add_edge(1, 3);

    hamiltonian::Config config;
    config.algorithm = hamiltonian::Algorithm::HeldKarp;
    config.timeout = std::chrono::milliseconds(5000);

    hamiltonian::Solver solver(config);
    hamiltonian::Result res = solver.solve(g);

    if (res.status == hamiltonian::Status::Success) {
        std::cout << "Гамільтонів цикл знайдено (вершин " << res.path.size() << "):\n";
        for (size_t v : res.path) {
            std::cout << v << " ";
        }
        std::cout << "\nВитрачено часу: " << res.elapsed_time.count() 
                  << "s, досліджені стани: " << res.states_explored << "\n";
    } else {
        std::cout << "Гамільтонів цикл відсутній.\n";
    }

    return 0;
}
