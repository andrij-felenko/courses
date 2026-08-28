/* C API: Повний заголовочний файл бібліотеки libbipartite */
#ifndef BIPARTITE_GRAPH_H
#define BIPARTITE_GRAPH_H

#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef enum {
    BIPARTITE_OK                         =  0,
    BIPARTITE_ERR_NOT_BIPARTITE          = -1,
    BIPARTITE_ERR_INVALID_PARTITION      = -2,
    BIPARTITE_ERR_INDEX_OUT_OF_BOUNDS    = -3,
    BIPARTITE_ERR_NULL_POINTER           = -4,
    BIPARTITE_ERR_NO_MEMORY              = -5
} bipartite_status_t;

typedef struct {
    size_t num_left;        /* Кількість вершин у лівій частці U (|U| = n₁) */
    size_t num_right;       /* Кількість вершин у правій частці V (|V| = n₂) */
    size_t num_edges;       /* Загальна кількість ребер |E| */
    size_t **adj_left;      /* Динамічний масив списків суміжності для U */
    size_t *deg_left;       /* Поточний ступінь кожної вершини U */
    size_t *cap_left;       /* Виділена ємність списків суміжності для U */
    size_t **adj_right;     /* Динамічний масив списків суміжності для V */
    size_t *deg_right;      /* Поточний ступінь кожної вершини V */
    size_t *cap_right;      /* Виділена ємність списків суміжності для V */
} bipartite_graph_t;

#ifdef __cplusplus
}
#endif

#endif /* BIPARTITE_GRAPH_H */
