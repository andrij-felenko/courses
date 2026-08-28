#include <stdio.h>
#include <stdlib.h>
#include "euler_api.h"

int main(void) {
    euler_graph_t* graph = NULL;
    euler_status_t status;

    /* 1. Створення орієнтованого графа з 4 вершинами */
    status = euler_graph_create(4, EULER_GRAPH_DIRECTED, &graph);
    if (status != EULER_SUCCESS) {
        fprintf(stderr, "Помилка створення графа: %d\n", status);
        return EXIT_FAILURE;
    }

    /* 2. Додавання ребер: 0->1->2->3->0 та 1->3->1 */
    euler_graph_add_edge(graph, 0, 1, 1, NULL);
    euler_graph_add_edge(graph, 1, 2, 1, NULL);
    euler_graph_add_edge(graph, 2, 3, 1, NULL);
    euler_graph_add_edge(graph, 3, 0, 1, NULL);
    euler_graph_add_edge(graph, 1, 3, 1, NULL);
    euler_graph_add_edge(graph, 3, 1, 1, NULL);

    /* 3. Пошук ейлерового циклу */
    euler_result_t result;
    status = euler_graph_find_circuit(graph, 0, &result);

    if (status == EULER_SUCCESS) {
        printf("Ейлерів цикл успішно знайдено (довжина %d вершин):\n", result.length);
        for (int i = 0; i < result.length; i++) {
            printf("%d%s", result.path_vertices[i], (i == result.length - 1) ? "\n" : " -> ");
        }
        euler_result_free(&result);
    } else {
        printf("Не вдалося побудувати ейлерів цикл, код помилки: %d\n", status);
    }

    /* 4. Звільнення ресурсів */
    euler_graph_free(graph);
    return EXIT_SUCCESS;
}
