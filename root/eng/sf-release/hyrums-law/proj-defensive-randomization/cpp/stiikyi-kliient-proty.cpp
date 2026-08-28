/* Клієнтська логіка на C++ */
#include <algorithm>
#include <iostream>

void robust_client_process(NodeRegistry& registry) {
    std::vector<ClusterNode> nodes = registry.get_active_nodes();

    /* СТІЙКИЙ ПІДХІД: якщо клієнту потрібен детермінований порядок,
       він явно сортує колекцію за ідентифікатором або назвою */
    std::sort(nodes.begin(), nodes.end(), [](const auto& a, const auto& b) {
        return a.node_id < b.node_id;
    });

    for (const auto& node : nodes) {
        // Гарантована детермінована обробка незалежно від поведінки API
    }
}
