#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

// Структура представлення зваженого ребра
typedef struct {
    uint32_t u;
    uint32_t v;
    int64_t weight;
} Edge;

// Структура системи неперетинних множин (DSU)
typedef struct {
    uint32_t *parent;
    uint8_t *rank;
    uint32_t num_sets;
} Dsu;

// Ініціалізація DSU
static bool dsu_init(Dsu *dsu, uint32_t n) {
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
    dsu->num_sets = n;
    return true;
}

static void dsu_free(Dsu *dsu) {
    free(dsu->parent);
    free(dsu->rank);
    dsu->parent = NULL;
    dsu->rank = NULL;
}

// Пошук представника множини зі стисненням шляху без рекурсії
static uint32_t dsu_find(Dsu *dsu, uint32_t i) {
    uint32_t root = i;
    while (root != dsu->parent[root]) {
        root = dsu->parent[root];
    }
    // Другий прохід: стиснення шляху
    uint32_t curr = i;
    while (curr != root) {
        uint32_t nxt = dsu->parent[curr];
        dsu->parent[curr] = root;
        curr = nxt;
    }
    return root;
}

// Об'єднання за рангом
static bool dsu_union(Dsu *dsu, uint32_t i, uint32_t j) {
    uint32_t root_i = dsu_find(dsu, i);
    uint32_t root_j = dsu_find(dsu, j);
    if (root_i == root_j) {
        return false; // Вже в одній компоненті (цикл)
    }

    if (dsu->rank[root_i] < dsu->rank[root_j]) {
        dsu->parent[root_i] = root_j;
    } else if (dsu->rank[root_i] > dsu->rank[root_j]) {
        dsu->parent[root_j] = root_i;
    } else {
        dsu->parent[root_j] = root_i;
        dsu->rank[root_i]++;
    }
    dsu->num_sets--;
    return true;
}

// Компаратор для швидкого сортування ребер
static int edge_compare(const void *a, const void *b) {
    const Edge *ea = (const Edge *)a;
    const Edge *eb = (const Edge *)b;
    if (ea->weight < eb->weight) return -1;
    if (ea->weight > eb->weight) return 1;
    return 0;
}

// Результат виконання алгоритму Краскала
typedef struct {
    Edge *mst_edges;
    size_t edge_count;
    int64_t total_weight;
    bool is_fully_connected;
} KruskalResult;

KruskalResult kruskal_solve(uint32_t num_vertices, Edge *edges, size_t num_edges) {
    KruskalResult res = { NULL, 0, 0, false };
    if (num_vertices == 0) {
        res.is_fully_connected = true;
        return res;
    }

    res.mst_edges = (Edge *)malloc((num_vertices - 1) * sizeof(Edge));
    if (!res.mst_edges && num_vertices > 1) {
        return res;
    }

    // Крок 1: Глобальне сортування ребер
    qsort(edges, num_edges, sizeof(Edge), edge_compare);

    // Крок 2: Ініціалізація DSU
    Dsu dsu;
    if (!dsu_init(&dsu, num_vertices)) {
        free(res.mst_edges);
        res.mst_edges = NULL;
        return res;
    }

    // Крок 3: Жадібний вибір ребер
    for (size_t i = 0; i < num_edges; ++i) {
        if (dsu_union(&dsu, edges[i].u, edges[i].v)) {
            res.mst_edges[res.edge_count++] = edges[i];
            res.total_weight += edges[i].weight;

            // Оптимізація раннього виходу
            if (res.edge_count == num_vertices - 1) {
                break;
            }
        }
    }

    res.is_fully_connected = (res.edge_count == num_vertices - 1);
    dsu_free(&dsu);
    return res;
}
