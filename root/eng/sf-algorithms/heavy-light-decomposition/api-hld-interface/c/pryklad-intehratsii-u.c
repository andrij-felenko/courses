#include <stdio.h>
#include <assert.h>

int main(void) {
    hld_tree_t router_tree;
    int node_count = 6;
    int root_gateway = 0;

    /* Ініціалізація дерева маршрутизації */
    int rc = hld_init(&router_tree, node_count, root_gateway);
    assert(rc == HLD_SUCCESS);

    /* Топологія: 0-1, 0-2, 1-3, 1-4, 2-5 */
    hld_add_edge(&router_tree, 0, 1);
    hld_add_edge(&router_tree, 0, 2);
    hld_add_edge(&router_tree, 1, 3);
    hld_add_edge(&router_tree, 1, 4);
    hld_add_edge(&router_tree, 2, 5);

    /* Початкове навантаження на маршрутизаторах (Мбіт/с) */
    hld_set_node_val(&router_tree, 0, 100);
    hld_set_node_val(&router_tree, 1, 50);
    hld_set_node_val(&router_tree, 2, 80);
    hld_set_node_val(&router_tree, 3, 20);
    hld_set_node_val(&router_tree, 4, 30);
    hld_set_node_val(&router_tree, 5, 40);

    /* Компіляція HLD */
    rc = hld_build(&router_tree);
    assert(rc == HLD_SUCCESS);

    /* Перевірка найменшого спільного шлюзу (LCA) для 3 та 5 */
    int lca = hld_lca(&router_tree, 3, 5);
    assert(lca == 0);

    /* Запит сумарного трафіку на магістралі між вузлами 3 та 5 */
    /* Шлях: 3 -> 1 -> 0 -> 2 -> 5: 20 + 50 + 100 + 80 + 40 = 290 */
    int64_t total_traffic = hld_query_path(&router_tree, 3, 5);
    assert(total_traffic == 290);

    /* Динамічне збільшення трафіку у піддереві маршрутизатора 1 (+15 Мбіт/с) */
    hld_update_subtree(&router_tree, 1, 15);

    /* Новий трафік піддерева 1: (50+15) + (20+15) + (30+15) = 145 */
    int64_t subtree_traffic = hld_query_subtree(&router_tree, 1);
    assert(subtree_traffic == 145);

    printf("Усі перевірки системного HLD API пройдено успішно.\n");
    return 0;
}
