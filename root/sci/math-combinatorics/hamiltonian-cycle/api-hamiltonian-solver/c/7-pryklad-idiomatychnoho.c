#include "libhamiltonian.h"
#include <stdio.h>

int main(void) {
    size_t n = 5;
    hamiltonian_graph_t *g = hamiltonian_graph_create(n);
    if (!g) return 1;

    /* Створення циклу 0-1-2-3-4-0 з додатковими хордами */
    hamiltonian_graph_add_edge(g, 0, 1);
    hamiltonian_graph_add_edge(g, 1, 2);
    hamiltonian_graph_add_edge(g, 2, 3);
    hamiltonian_graph_add_edge(g, 3, 4);
    hamiltonian_graph_add_edge(g, 4, 0);
    hamiltonian_graph_add_edge(g, 1, 3);

    hamiltonian_config_t config;
    hamiltonian_config_init_default(&config);
    config.algorithm = HAMILTONIAN_ALGO_HELD_KARP;

    hamiltonian_result_t result;
    hamiltonian_status_t st = hamiltonian_solve(g, &config, &result);

    if (st == HAMILTONIAN_SUCCESS) {
        printf("Гамільтонів цикл знайдено (вершин %zu):\n", result.path_length);
        for (size_t i = 0; i < result.path_length; ++i) {
            printf("%zu ", result.path[i]);
        }
        printf("\nВитрачено часу: %.6f сек, станів: %lu\n", 
               result.elapsed_seconds, (unsigned long)result.states_explored);
    } else {
        printf("Гамільтонів цикл відсутній або сталася помилка: %d\n", st);
    }

    hamiltonian_result_free(&result);
    hamiltonian_graph_free(g);
    return 0;
}
