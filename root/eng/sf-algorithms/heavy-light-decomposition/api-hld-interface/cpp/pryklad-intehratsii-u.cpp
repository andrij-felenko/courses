#include <iostream>
#include <cassert>

int main() {
    constexpr int node_count = 6;
    constexpr int root_gateway = 0;

    HeavyLightDecomposition<int64_t> router_tree(node_count, root_gateway);

    /* Топологія: 0-1, 0-2, 1-3, 1-4, 2-5 */
    router_tree.add_edge(0, 1);
    router_tree.add_edge(0, 2);
    router_tree.add_edge(1, 3);
    router_tree.add_edge(1, 4);
    router_tree.add_edge(2, 5);

    /* Початкове навантаження на маршрутизаторах (Мбіт/с) */
    router_tree.set_value(0, 100);
    router_tree.set_value(1, 50);
    router_tree.set_value(2, 80);
    router_tree.set_value(3, 20);
    router_tree.set_value(4, 30);
    router_tree.set_value(5, 40);

    /* Компіляція HLD */
    router_tree.build(root_gateway);

    /* Перевірка найменшого спільного шлюзу (LCA) */
    assert(router_tree.find_lca(3, 5) == 0);

    /* Запит сумарного трафіку на магістралі між вузлами 3 та 5 */
    int64_t total_traffic = router_tree.query_path(3, 5);
    assert(total_traffic == 290);

    /* Динамічне збільшення трафіку у піддереві маршрутизатора 1 (+15 Мбіт/с) */
    router_tree.update_subtree(1, 15);

    /* Новий трафік піддерева 1 */
    int64_t subtree_traffic = router_tree.query_subtree(1);
    assert(subtree_traffic == 145);

    std::cout << "Усі перевірки C++ HLD API пройдено успішно.\n";
    return 0;
}
