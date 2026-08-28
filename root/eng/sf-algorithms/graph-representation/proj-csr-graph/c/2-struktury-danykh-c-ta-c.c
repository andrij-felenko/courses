#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Динамічний масив для списку суміжності однієї вершини */
typedef struct {
    uint32_t *data;
    size_t size;
    size_t capacity;
} AdjArray;

typedef struct {
    uint32_t num_vertices;
    AdjArray *adj;
} DynamicGraph;

/* Створення динамічного графа */
DynamicGraph* dynamic_graph_create(uint32_t num_vertices) {
    DynamicGraph *g = (DynamicGraph*)malloc(sizeof(DynamicGraph));
    g->num_vertices = num_vertices;
    g->adj = (AdjArray*)calloc(num_vertices, sizeof(AdjArray));
    return g;
}

/* Додавання орієнтованого ребра u -> v */
void dynamic_graph_add_edge(DynamicGraph *g, uint32_t u, uint32_t v) {
    if (u >= g->num_vertices) return;
    AdjArray *arr = &g->adj[u];
    if (arr->size == arr->capacity) {
        size_t new_cap = (arr->capacity == 0) ? 2 : arr->capacity * 2;
        uint32_t *new_data = (uint32_t*)realloc(arr->data, new_cap * sizeof(uint32_t));
        if (!new_data) return;
        arr->data = new_data;
        arr->capacity = new_cap;
    }
    arr->data[arr->size++] = v;
}

void dynamic_graph_free(DynamicGraph *g) {
    if (!g) return;
    for (uint32_t i = 0; i < g->num_vertices; ++i) {
        free(g->adj[i].data);
    }
    free(g->adj);
    free(g);
}

/* Статичний незмінний граф у форматі Compressed Sparse Row (CSR) */
typedef struct {
    uint32_t num_vertices;
    size_t num_edges;
    uint32_t *offsets; /* Розмір: num_vertices + 1 */
    uint32_t *edges;   /* Розмір: num_edges */
} CsrGraph;

/* Конвертація динамічного графа в компактний CSR */
CsrGraph* csr_graph_from_dynamic(const DynamicGraph *dg) {
    CsrGraph *csr = (CsrGraph*)malloc(sizeof(CsrGraph));
    csr->num_vertices = dg->num_vertices;

    /* Підрахунок загальної кількості ребер */
    size_t total_edges = 0;
    for (uint32_t i = 0; i < dg->num_vertices; ++i) {
        total_edges += dg->adj[i].size;
    }
    csr->num_edges = total_edges;

    csr->offsets = (uint32_t*)malloc((dg->num_vertices + 1) * sizeof(uint32_t));
    csr->edges = (uint32_t*)malloc(total_edges * sizeof(uint32_t));

    uint32_t current_offset = 0;
    for (uint32_t i = 0; i < dg->num_vertices; ++i) {
        csr->offsets[i] = current_offset;
        const AdjArray *arr = &dg->adj[i];
        for (size_t j = 0; j < arr->size; ++j) {
            csr->edges[current_offset++] = arr->data[j];
        }
    }
    csr->offsets[dg->num_vertices] = current_offset;

    return csr;
}

void csr_graph_free(CsrGraph *csr) {
    if (!csr) return;
    free(csr->offsets);
    free(csr->edges);
    free(csr);
}
