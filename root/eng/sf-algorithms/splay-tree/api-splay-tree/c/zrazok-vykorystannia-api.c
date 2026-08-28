#include "splay_tree.h"
#include <stdio.h>

int main(void) {
    splay_tree_t *cache = splay_tree_create();

    /* Вставка даних */
    splay_tree_insert(cache, 19216801, 80);   /* IP 192.168.0.1 -> Port 80 */
    splay_tree_insert(cache, 10000001, 443);  /* IP 10.0.0.1 -> Port 443 */
    splay_tree_insert(cache, 17216001, 8080); /* IP 172.16.0.1 -> Port 8080 */

    /* Швидкий доступ до гарячого ключа */
    int port = 0;
    if (splay_tree_find(cache, 10000001, &port)) {
        printf("Знайдено порт: %d (вузол піднято в корінь)\n", port);
    }

    /* Наступне звернення до того самого ключа виконається за O(1) */
    splay_tree_find(cache, 10000001, &port);

    splay_tree_destroy(cache);
    return 0;
}
