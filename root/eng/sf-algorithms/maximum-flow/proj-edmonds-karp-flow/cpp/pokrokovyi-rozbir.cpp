int main() {
    // Створюємо мережу на 6 вершин (0..5)
    EdmondsKarp<int64_t> network(6);

    // Додаємо канали зв'язку: (from, to, capacity)
    network.add_edge(0, 1, 10);
    network.add_edge(0, 2, 10);
    network.add_edge(1, 2, 2);
    network.add_edge(1, 3, 4);
    network.add_edge(1, 4, 8);
    network.add_edge(2, 4, 9);
    network.add_edge(3, 5, 10);
    network.add_edge(4, 5, 10);

    // 1. Обчислюємо максимальний потік
    int64_t max_val = network.max_flow(0, 5);
    std::cout << "Максимальний потік: " << max_val << "\n";

    // 2. Отримуємо мінімальний розріз
    std::vector<bool> in_source_component = network.min_cut(0);

    std::cout << "Критичні ребра мінімального розрізу (S -> T):\n";
    for (int u = 0; u < network.vertex_count(); ++u) {
        if (!in_source_component[u]) continue;
        for (const auto& edge : network.get_edges(u)) {
            // Пряме ребро з S у T, яке було спочатку присутнє у графі
            if (!in_source_component[edge.to] && edge.cap > 0) {
                std::cout << "  Ребро " << u << " -> " << edge.to 
                          << " (насичено " << edge.flow << "/" << edge.cap << ")\n";
            }
        }
    }

    return 0;
}
