#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/* Умовний заголовок бібліотеки planar_graph.h */

int main(void) {
    PlanarGraph* g = NULL;
    
    /* Створюємо граф: октаедр (6 вершин, 12 ребер, 8 граней) */
    if (planar_graph_create(&g, 6, 12) != PLANAR_OK) {
        fprintf(stderr, "Помилка виділення пам'яті\n");
        return EXIT_FAILURE;
    }

    /* Додаємо ребра екваторіального квадрата */
    planar_graph_add_edge(g, 0, 1, NULL);
    planar_graph_add_edge(g, 1, 2, NULL);
    planar_graph_add_edge(g, 2, 3, NULL);
    planar_graph_add_edge(g, 3, 0, NULL);

    /* Додаємо ребра до північного полюса (вершина 4) */
    planar_graph_add_edge(g, 4, 0, NULL);
    planar_graph_add_edge(g, 4, 1, NULL);
    planar_graph_add_edge(g, 4, 2, NULL);
    planar_graph_add_edge(g, 4, 3, NULL);

    /* Додаємо ребра до південного полюса (вершина 5) */
    planar_graph_add_edge(g, 5, 0, NULL);
    planar_graph_add_edge(g, 5, 1, NULL);
    planar_graph_add_edge(g, 5, 2, NULL);
    planar_graph_add_edge(g, 5, 3, NULL);

    /* 1. Лінійна перевірка планарності */
    bool is_planar = false;
    if (planar_graph_check_planarity(g, &is_planar) == PLANAR_OK && is_planar) {
        printf("Граф є планарним!\n");

        /* 2. Побудова комбінаторного вкладення */
        planar_graph_compute_embedding(g);

        /* 3. Виділення граней */
        planar_graph_extract_faces(g);
        printf("Вершин: %d, Ребер: %d, Граней: %d\n",
               g->num_vertices, g->num_edges, g->num_faces);
        printf("Баланс Ейлера V - E + F = %d (очікується 2)\n",
               g->num_vertices - g->num_edges + g->num_faces);
    } else {
        printf("Граф не є планарним!\n");
    }

    /* 4. Звільнення ресурсів */
    planar_graph_destroy(g);
    return EXIT_SUCCESS;
}
