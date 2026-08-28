#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Непрозорий тип графа */
typedef struct Graph Graph;

/* Створення графа з фіксованою або початковою кількістю вершин */
Graph* graph_create(uint32_t num_vertices, bool is_directed);
void   graph_destroy(Graph *g);

/* Топологічні запити розміру */
uint32_t graph_vertex_count(const Graph *g);
size_t   graph_edge_count(const Graph *g);
bool     graph_is_directed(const Graph *g);

/* Модифікація зв'язків */
bool graph_add_edge(Graph *g, uint32_t u, uint32_t v, double weight);
bool graph_remove_edge(Graph *g, uint32_t u, uint32_t v);
bool graph_add_vertex(Graph *g, uint32_t *out_vertex_id);
bool graph_remove_vertex(Graph *g, uint32_t u);

/* Запити суміжності */
bool   graph_has_edge(const Graph *g, uint32_t u, uint32_t v);
double graph_get_edge_weight(const Graph *g, uint32_t u, uint32_t v);
bool   graph_set_edge_weight(Graph *g, uint32_t u, uint32_t v, double weight);

/* Ступені вершин */
uint32_t graph_out_degree(const Graph *g, uint32_t u);
uint32_t graph_in_degree(const Graph *g, uint32_t u);

/* Ітератор по вихідних сусідах */
typedef struct {
    const Graph *graph;
    uint32_t vertex;
    size_t state_cursor;
} GraphNeighborIter;

GraphNeighborIter graph_neighbors_begin(const Graph *g, uint32_t u);
bool graph_neighbors_next(GraphNeighborIter *it, uint32_t *out_target, double *out_weight);
