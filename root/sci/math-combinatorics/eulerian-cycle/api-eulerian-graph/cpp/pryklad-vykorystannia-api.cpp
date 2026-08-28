#include <iostream>
#include "euler_api.hpp"

int main() {
    try {
        // 1. Створення орієнтованого графа з 4 вершинами (RAII)
        euler::EulerianGraph graph(4, euler::GraphType::Directed);

        // 2. Додавання ребер: 0->1->2->3->0 та 1->3->1
        graph.add_edge(0, 1);
        graph.add_edge(1, 2);
        graph.add_edge(2, 3);
        graph.add_edge(3, 0);
        graph.add_edge(1, 3);
        graph.add_edge(3, 1);

        // 3. Пошук ейлерового циклу через std::optional
        if (auto result = graph.find_circuit(0)) {
            std::cout << "Ейлерів цикл успішно знайдено (довжина " 
                      << result->vertices.size() << " вершин):\n";
            for (std::size_t i = 0; i < result->vertices.size(); ++i) {
                std::cout << result->vertices[i] 
                          << (i == result->vertices.size() - 1 ? "\n" : " -> ");
            }
        } else {
            std::cout << "Граф не містить ейлерового циклу.\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "Системна помилка: " << ex.what() << "\n";
        return EXIT_FAILURE;
    }
    return EXIT_SUCCESS;
}
