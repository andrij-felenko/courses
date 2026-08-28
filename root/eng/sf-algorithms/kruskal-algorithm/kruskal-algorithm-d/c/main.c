#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

// Опис зваженого ребра графа
typedef struct {
    uint32_t u;
    uint32_t v;
    int64_t weight;
} Edge;

// Система неперетинних множин (DSU)
typedef struct {
    uint32_t *parent;
    uint8_t *rank;
    uint32_t count;
} DisjointSet;

static bool dsu_create(DisjointSet *dsu, uint32_t n) {
    dsu->parent = (uint32_t *)malloc(n * sizeof(uint32_t));
    dsu->rank = (uint8_t *)calloc(n, sizeof(uint8_t));
    if (!dsu->parent || !dsu->rank) {
        free(dsu->parent);
        free(dsu->rank);
        return false;
    }
    for (uint32_t i = 0; i < n; ++i) {
        dsu->parent[i] = i;
    }
    dsu->count = n;
    return true;
}

static void dsu_destroy(DisjointSet *dsu) {
    free(dsu->parent);
    free(dsu->rank);
    dsu->parent = NULL;
    dsu->rank = NULL;
}

// Пошук кореневого представника зі стисненням шляху
static uint32_t dsu_find_root(DisjointSet *dsu, uint32_t i) {
    uint32_t root = i;
    while (root != dsu->parent[root]) {
        root = dsu->parent[root];
    }
    // Двопрохідне стиснення шляху: переприв'язка на знайдений корінь
    uint32_t curr = i;
    while (curr != root) {
        uint32_t next = dsu->parent[curr];
        dsu->parent[curr] = root;
        curr = next;
    }
    return root;
}

// Об'єднання двох множин за рангом
static bool dsu_unite(DisjointSet *dsu, uint32_t i, uint32_t j) {
    uint32_t root_i = dsu_find_root(dsu, i);
    uint32_t root_j = dsu_find_root(dsu, j);
    if (root_i == root_j) {
        return false; // Вершини в одній компоненті (утворення циклу)
    }

    if (dsu->rank[root_i] < dsu->rank[root_j]) {
        dsu->parent[root_i] = root_j;
    } else if (dsu->rank[root_i] > dsu->rank[root_j]) {
        dsu->parent[root_j] = root_i;
    } else {
        dsu->parent[root_j] = root_i;
        dsu->rank[root_i]++;
    }
    dsu->count--;
    return true;
}

// Компаратор для сортування масиву ребер
static int compare_edges(const void *a, const void *b) {
    const Edge *ea = (const Edge *)a;
    const Edge *eb = (const Edge *)b;
    if (ea->weight < eb->weight) return -1;
    if (ea->weight > eb->weight) return 1;
    return 0;
}

// Структура результату виконання
typedef struct {
    Edge *tree_edges;
    size_t num_edges;
    int64_t total_weight;
    bool is_connected;
} MstOutput;

MstOutput kruskal_find_mst(uint32_t num_vertices, Edge *edges, size_t num_edges) {
    MstOutput out = { NULL, 0, 0, false };
    if (num_vertices == 0) {
        out.is_connected = true;
        return out;
    }

    out.tree_edges = (Edge *)malloc((num_vertices - 1) * sizeof(Edge));
    if (!out.tree_edges && num_vertices > 1) {
        return out;
    }

    // Фаза 1: Глобальне сортування ребер
    qsort(edges, num_edges, sizeof(Edge), compare_edges);

    // Фаза 2: Ініціалізація DSU
    DisjointSet dsu;
    if (!dsu_create(&dsu, num_vertices)) {
        free(out.tree_edges);
        out.tree_edges = NULL;
        return out;
    }

    // Фаза 3: Жадібний відбір ребер
    for (size_t i = 0; i < num_edges; ++i) {
        if (dsu_unite(&dsu, edges[i].u, edges[i].v)) {
            out.tree_edges[out.num_edges++] = edges[i];
            out.total_weight += edges[i].weight;

            // Ранній вихід: кістяк набрано
            if (out.num_edges == num_vertices - 1) {
                break;
            }
        }
    }

    out.is_connected = (out.num_edges == num_vertices - 1);
    dsu_destroy(&dsu);
    return out;
}
