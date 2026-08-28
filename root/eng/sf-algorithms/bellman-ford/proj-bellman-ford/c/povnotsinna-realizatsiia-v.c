#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <limits.h>

#define INF LLONG_MAX

// Структура орієнтованого ребра
typedef struct {
    int src;
    int dest;
    long long weight;
} Edge;

// Результат роботи алгоритму
typedef struct {
    long long* dist;
    int* parent;
    bool has_negative_cycle;
    int cycle_start_node;
    int num_vertices;
} BellmanFordResult;

// Ініціалізація структури результату
BellmanFordResult create_result(int V) {
    BellmanFordResult res;
    res.num_vertices = V;
    res.dist = (long long*)malloc(V * sizeof(long long));
    res.parent = (int*)malloc(V * sizeof(int));
    res.has_negative_cycle = false;
    res.cycle_start_node = -1;

    for (int i = 0; i < V; ++i) {
        res.dist[i] = INF;
        res.parent[i] = -1;
    }
    return res;
}

// Звільнення ресурсів
void free_result(BellmanFordResult* res) {
    if (res->dist) free(res->dist);
    if (res->parent) free(res->parent);
    res->dist = NULL;
    res->parent = NULL;
}

// Головна функція алгоритму Беллмана-Форда
BellmanFordResult bellman_ford(int num_vertices, int num_edges, const Edge* edges, int start_node) {
    BellmanFordResult res = create_result(num_vertices);
    res.dist[start_node] = 0;

    // Фаза 1: V - 1 раундів релаксації
    for (int iter = 0; iter < num_vertices - 1; ++iter) {
        bool updated = false;
        for (int e = 0; e < num_edges; ++e) {
            int u = edges[e].src;
            int v = edges[e].dest;
            long long w = edges[e].weight;

            if (res.dist[u] != INF && res.dist[u] + w < res.dist[v]) {
                res.dist[v] = res.dist[u] + w;
                res.parent[v] = u;
                updated = true;
            }
        }
        // Оптимізація раннього виходу при збіжності
        if (!updated) {
            break;
        }
    }

    // Фаза 2: V-й раунд для перевірки від'ємних циклів
    for (int e = 0; e < num_edges; ++e) {
        int u = edges[e].src;
        int v = edges[e].dest;
        long long w = edges[e].weight;

        if (res.dist[u] != INF && res.dist[u] + w < res.dist[v]) {
            res.has_negative_cycle = true;
            res.cycle_start_node = v;
            break;
        }
    }

    return res;
}

// Відновлення найкоротшого шляху до вершини target
void print_path(const BellmanFordResult* res, int target) {
    if (res->dist[target] == INF) {
        printf("Шлях відсутній (вершина недосяжна)\n");
        return;
    }

    int curr = target;
    int path[1024];
    int count = 0;

    while (curr != -1) {
        path[count++] = curr;
        curr = res->parent[curr];
    }

    printf("Шлях (вага %lld): ", res->dist[target]);
    for (int i = count - 1; i >= 0; --i) {
        printf("%d%s", path[i], (i > 0) ? " -> " : "\n");
    }
}

int main(void) {
    int V = 5;
    Edge edges[] = {
        {0, 1, 4},
        {0, 2, 5},
        {1, 3, 3},
        {2, 1, -6},
        {3, 2, 1}
    };
    int E = sizeof(edges) / sizeof(edges[0]);

    BellmanFordResult res = bellman_ford(V, E, edges, 0);

    if (res.has_negative_cycle) {
        printf("Увага: виявлено від'ємний цикл у графі!\n");
    } else {
        printf("Результати розрахунку найкоротших шляхів:\n");
        for (int i = 0; i < V; ++i) {
            printf("До вершини %d: ", i);
            print_path(&res, i);
        }
    }

    free_result(&res);
    return 0;
}
