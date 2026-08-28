#include <iostream>
#include <memory>

int main() {
    // Створюємо граф октаедра (6 вершин)
    auto graph_result = create_planar_graph(6, 12);
    if (!graph_result) {
        std::cerr << "Помилка створення графа\n";
        return 1;
    }

    auto g = std::move(graph_result.value());

    // Екваторіальний контур
    g->add_edge(0, 1);
    g->add_edge(1, 2);
    g->add_edge(2, 3);
    g->add_edge(3, 0);

    // Зв'язки з північним полюсом
    g->add_edge(4, 0);
    g->add_edge(4, 1);
    g->add_edge(4, 2);
    g->add_edge(4, 3);

    // Зв'язки з південним полюсом
    g->add_edge(5, 0);
    g->add_edge(5, 1);
    g->add_edge(5, 2);
    g->add_edge(5, 3);

    // 1. Перевірка планарності
    auto planarity = g->check_planarity();
    if (planarity && *planarity) {
        std::cout << "Граф є планарним!\n";

        // 2. Побудова системи ротацій
        g->compute_embedding();

        // 3. Виділення граней
        auto faces = g->extract_faces();
        if (faces) {
            std::cout << "Вершин: " << g->vertex_count()
                      << ", Ребер: " << g->edge_count()
                      << ", Граней: " << faces->size() << "\n";
            std::cout << "Баланс Ейлера: "
                      << g->vertex_count() - g->edge_count() + faces->size()
                      << " (очікується 2)\n";
        }
    }

    return 0;
}
