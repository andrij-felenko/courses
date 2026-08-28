#ifndef LIBHAMILTONIAN_H
#define LIBHAMILTONIAN_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct hamiltonian_graph hamiltonian_graph_t;

/* Створення нового графа на num_vertices вершин */
hamiltonian_graph_t* hamiltonian_graph_create(size_t num_vertices);

/* Звільнення ресурсів графа */
void hamiltonian_graph_free(hamiltonian_graph_t *graph);

/* Додавання неупорядкованого ребра між u та v */
hamiltonian_status_t hamiltonian_graph_add_edge(hamiltonian_graph_t *graph, size_t u, size_t v);

/* Ініціалізація структури конфігурації параметрами за замовчуванням */
void hamiltonian_config_init_default(hamiltonian_config_t *config);

/* Основна функція розв'язання задачі гамільтонового циклу */
hamiltonian_status_t hamiltonian_solve(
    const hamiltonian_graph_t *graph,
    const hamiltonian_config_t *config,
    hamiltonian_result_t *out_result
);

/* Звільнення внутрішніх ресурсів структури результату */
void hamiltonian_result_free(hamiltonian_result_t *result);

/* Допоміжна перевірка достатніх умов Дірака (O(V)) */
bool hamiltonian_check_dirac_condition(const hamiltonian_graph_t *graph);

/* Допоміжна перевірка достатніх умов Оре (O(V²)) */
bool hamiltonian_check_ore_condition(const hamiltonian_graph_t *graph);

#ifdef __cplusplus
}
#endif

#endif /* LIBHAMILTONIAN_H */
