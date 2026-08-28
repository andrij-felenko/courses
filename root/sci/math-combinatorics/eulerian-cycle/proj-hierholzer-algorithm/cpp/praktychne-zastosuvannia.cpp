#include <iostream>
#include <vector>
#include <string>
#include <cmath>

std::string generate_debruijn_sequence(int n) {
    if (n <= 0) return "";
    if (n == 1) return "01";

    int num_states = 1 << (n - 1); // 2^(n-1) вершин
    EulerianSolver solver(num_states);

    // Будуємо ребра графа де Брейнена: з стану (b1 b2 ... bn-1) в стан (b2 ... bn-1 0) та (b2 ... bn-1 1)
    for (int i = 0; i < num_states; ++i) {
        int next_state_0 = (i << 1) & (num_states - 1);
        int next_state_1 = next_state_0 | 1;
        solver.add_edge(i, next_state_0);
        solver.add_edge(i, next_state_1);
    }

    auto path = solver.find_eulerian_circuit(0);
    if (!path) return "";

    std::string result;
    result.reserve((1 << n) + n - 1);
    
    // Початкові біти першого стану
    for (int i = 0; i < n - 1; ++i) {
        result += '0';
    }

    // З кожного переходу беремо молодший біт нової вершини
    for (std::size_t i = 1; i < path->size(); ++i) {
        result += std::to_string((*path)[i] & 1);
    }

    return result;
}
