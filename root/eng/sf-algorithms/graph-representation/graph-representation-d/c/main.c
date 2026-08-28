#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

/* Проста черга FIFO для цілих чисел */
typedef struct {
    uint32_t *data;
    size_t head;
    size_t tail;
    size_t capacity;
} Queue;

Queue* queue_create(size_t capacity) {
    Queue *q = (Queue*)malloc(sizeof(Queue));
    q->data = (uint32_t*)malloc(capacity * sizeof(uint32_t));
    q->head = 0;
    q->tail = 0;
    q->capacity = capacity;
    return q;
}

void queue_push(Queue *q, uint32_t val) {
    q->data[q->tail++] = val;
}

uint32_t queue_pop(Queue *q) {
    return q->data[q->head++];
}

bool queue_is_empty(const Queue *q) {
    return q->head == q->tail;
}

void queue_free(Queue *q) {
    free(q->data);
    free(q);
}

/* 1. Пошук у ширину (BFS) на матриці суміжності: час O(V²) */
void bfs_matrix(const uint8_t *matrix, uint32_t num_vertices, uint32_t start_node) {
    bool *visited = (bool*)calloc(num_vertices, sizeof(bool));
    Queue *q = queue_create(num_vertices);

    visited[start_node] = true;
    queue_push(q, start_node);

    while (!queue_is_empty(q)) {
        uint32_t u = queue_pop(q);

        /* Скануємо весь рядок матриці довжиною num_vertices */
        for (uint32_t v = 0; v < num_vertices; ++v) {
            if (matrix[u * num_vertices + v] && !visited[v]) {
                visited[v] = true;
                queue_push(q, v);
            }
        }
    }

    queue_free(q);
    free(visited);
}

/* 2. Пошук у ширину (BFS) на списках суміжності: час O(V + E) */
typedef struct {
    uint32_t *neighbors;
    size_t count;
} AdjList;

void bfs_adj_list(const AdjList *adj, uint32_t num_vertices, uint32_t start_node) {
    bool *visited = (bool*)calloc(num_vertices, sizeof(bool));
    Queue *q = queue_create(num_vertices);

    visited[start_node] = true;
    queue_push(q, start_node);

    while (!queue_is_empty(q)) {
        uint32_t u = queue_pop(q);

        /* Скануємо лише реальних сусідів вершини u */
        const AdjList *list = &adj[u];
        for (size_t i = 0; i < list->count; ++i) {
            uint32_t v = list->neighbors[i];
            if (!visited[v]) {
                visited[v] = true;
                queue_push(q, v);
            }
        }
    }

    queue_free(q);
    free(visited);
}
