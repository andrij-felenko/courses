#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

#define INF INFINITY

/* Структура зваженої матриці суміжності графа */
typedef struct {
    size_t vertices;
    double* data; /* Неперервний масив розміру vertices * vertices */
} AdjMatrix;

/* Створення матриці суміжності */
AdjMatrix* adj_matrix_create(size_t vertices) {
    if (vertices == 0) return NULL;

    AdjMatrix* graph = (AdjMatrix*)malloc(sizeof(AdjMatrix));
    if (!graph) return NULL;

    graph->vertices = vertices;
    graph->data = (double*)malloc(vertices * vertices * sizeof(double));
    if (!graph->data) {
        free(graph);
        return NULL;
    }

    /* Ініціалізація: 0 на діагоналі, INF для відсутніх ребер */
    for (size_t i = 0; i < vertices; ++i) {
        for (size_t j = 0; j < vertices; ++j) {
            if (i == j) {
                graph->data[i * vertices + j] = 0.0;
            } else {
                graph->data[i * vertices + j] = INF;
            }
        }
    }

    return graph;
}

/* Звільнення пам'яті (RAII у стилі C) */
void adj_matrix_free(AdjMatrix* graph) {
    if (graph) {
        free(graph->data);
        free(graph);
    }
}

/* Додавання орієнтованого ребра з вагою */
bool adj_matrix_add_edge(AdjMatrix* graph, size_t u, size_t v, double weight) {
    if (!graph || u >= graph->vertices || v >= graph->vertices) {
        return false;
    }
    graph->data[u * graph->vertices + v] = weight;
    return true;
}

/* Перевірка наявності ребра O(1) */
bool adj_matrix_has_edge(const AdjMatrix* graph, size_t u, size_t v) {
    if (!graph || u >= graph->vertices || v >= graph->vertices) {
        return false;
    }
    double w = graph->data[u * graph->vertices + v];
    return !isnan(w) && w != INF;
}

/* Отримання ваги ребра */
double adj_matrix_get_weight(const AdjMatrix* graph, size_t u, size_t v) {
    if (!graph || u >= graph->vertices || v >= graph->vertices) {
        return INF;
    }
    return graph->data[u * graph->vertices + v];
}

/* Алгоритм Флойда — Уоршелла O(N³) над матрицею "на місці" */
bool adj_matrix_floyd_warshall(AdjMatrix* graph, double* dist_matrix) {
    if (!graph || !dist_matrix) return false;

    size_t n = graph->vertices;

    /* Скопіюємо початковий стан матриці */
    for (size_t i = 0; i < n * n; ++i) {
        dist_matrix[i] = graph->data[i];
    }

    /* Основний трикратний цикл Флойда — Уоршелла */
    for (size_t k = 0; k < n; ++k) {
        for (size_t i = 0; i < n; ++i) {
            for (size_t j = 0; j < n; ++j) {
                double ik = dist_matrix[i * n + k];
                double kj = dist_matrix[k * n + j];

                if (ik != INF && kj != INF) {
                    if (ik + kj < dist_matrix[i * n + j]) {
                        dist_matrix[i * n + j] = ik + kj;
                    }
                }
            }
        }
    }

    /* Перевірка на від'ємні цикли на діагоналі */
    for (size_t i = 0; i < n; ++i) {
        if (dist_matrix[i * n + i] < 0.0) {
            return false; /* Граф містить від'ємний цикл */
        }
    }

    return true;
}

int main(void) {
    size_t n = 4;
    AdjMatrix* g = adj_matrix_create(n);

    adj_matrix_add_edge(g, 0, 1, 5.0);
    adj_matrix_add_edge(g, 0, 3, 10.0);
    adj_matrix_add_edge(g, 1, 2, 3.0);
    adj_matrix_add_edge(g, 2, 3, 1.0);

    printf("Перевірка ребра (0 -> 1): %s\n", 
           adj_matrix_has_edge(g, 0, 1) ? "Є" : "Немає");
    printf("Перевірка ребра (1 -> 3): %s\n", 
           adj_matrix_has_edge(g, 1, 3) ? "Є" : "Немає");

    double* dist = (double*)malloc(n * n * sizeof(double));
    if (adj_matrix_floyd_warshall(g, dist)) {
        printf("Найкоротша відстань від 0 до 3: %.1f (очікується 9.0: 0->1->2->3)\n", 
               dist[0 * n + 3]);
    }

    free(dist);
    adj_matrix_free(g);
    return 0;
}
