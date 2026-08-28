// Приклад використання C++ API
#include "matching_solver.hpp"
#include <iostream>

int main() {
    using namespace graph::matching;

    Graph g(6); // Створення графа на 6 вершин
    g.add_edge(0, 1);
    g.add_edge(1, 2);
    g.add_edge(2, 3);
    g.add_edge(3, 4);
    g.add_edge(4, 5);
    g.add_edge(5, 0);

    auto result = g.solve(Algorithm::EdmondsBlossom);
    if (result) {
        std::cout << "Паросполучення знайдено! Розмір: " << result->size << "\n";
        std::cout << "Досконале: " << (result->is_perfect ? "Так" : "Ні") << "\n";
        for (const auto& edge : result->edges) {
            std::cout << "Ребро: (" << edge.u << ", " << edge.v << ")\n";
        }
    } else {
        std::cerr << "Помилка обчислення паросполучення!\n";
    }
    return 0;
}
