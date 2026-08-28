#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/* Структура для ребра в списку суміжності */
typedef struct EdgeNode {
    int to;
    int edge_id;
    struct EdgeNode* next;
} EdgeNode;

/* Структура графа */
typedef struct {
    int num_vertices;
    int num_edges;
    EdgeNode** head;
    int* out_degree;
    int* in_degree;
} Graph;

/* Створення графа */
Graph* graph_create(int vertices) {
    Graph* g = (Graph*)malloc(sizeof(Graph));
    g->num_vertices = vertices;
    g->num_edges = 0;
    g->head = (EdgeNode**)calloc(vertices, sizeof(EdgeNode*));
    g->out_degree = (int*)calloc(vertices, sizeof(int));
    g->in_degree = (int*)calloc(vertices, sizeof(int));
    return g;
}

/* Додавання орієнтованого ребра */
void graph_add_edge(Graph* g, int u, int v, int edge_id) {
    EdgeNode* node = (EdgeNode*)malloc(sizeof(EdgeNode));
    node->to = v;
    node->edge_id = edge_id;
    node->next = g->head[u];
    g->head[u] = node;
    g->out_degree[u]++;
    g->in_degree[v]++;
    g->num_edges++;
}

/* Звільнення пам'яті графа */
void graph_free(Graph* g) {
    for (int i = 0; i < g->num_vertices; i++) {
        EdgeNode* curr = g->head[i];
        while (curr) {
            EdgeNode* tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    free(g->head);
    free(g->out_degree);
    free(g->in_degree);
    free(g);
}

/* Структура для повернення результату */
typedef struct {
    int* path;
    int path_len;
    bool success;
} EulerianResult;

/* Ітеративна реалізація алгоритму Гіргольцера на C (без рекурсії) */
EulerianResult find_eulerian_circuit_c(Graph* g, int start_vertex) {
    EulerianResult res = { NULL, 0, false };

    /* 1. Перевірка необхідної умови балансу степеней */
    for (int i = 0; i < g->num_vertices; i++) {
        if (g->in_degree[i] != g->out_degree[i]) {
            return res; /* Баланс не дотримано — цикл не існує */
        }
    }

    /* Буфери стеків */
    int* curr_stack = (int*)malloc(sizeof(int) * (g->num_edges + 1));
    int curr_top = 0;

    int* circuit_stack = (int*)malloc(sizeof(int) * (g->num_edges + 1));
    int circuit_top = 0;

    bool* visited_edges = (bool*)calloc(g->num_edges, sizeof(bool));

    /* Додаємо початкову вершину */
    curr_stack[curr_top++] = start_vertex;

    while (curr_top > 0) {
        int u = curr_stack[curr_top - 1];

        /* Шукаємо перше невідвідане ребро у списку суміжності */
        EdgeNode* curr = g->head[u];
        while (curr && visited_edges[curr->edge_id]) {
            curr = curr->next;
            g->head[u] = curr; /* Оптимізація: пересуваємо head, усуваючи повторні перевірки */
        }

        if (curr) {
            /* Переходимо по ребрах далі */
            visited_edges[curr->edge_id] = true;
            int v = curr->to;
            g->head[u] = curr->next;
            curr_stack[curr_top++] = v;
        } else {
            /* Немає вихідних ребер — записуємо вершину у результат */
            circuit_stack[circuit_top++] = u;
            curr_top--;
        }
    }

    free(visited_edges);
    free(curr_stack);

    /* Перевірка на зв'язність ребер: шлях повинен містити нуль або num_edges + 1 вершин */
    if (circuit_top != g->num_edges + 1) {
        free(circuit_stack);
        return res;
    }

    /* Реверсуємо масив результату */
    res.path = (int*)malloc(sizeof(int) * circuit_top);
    res.path_len = circuit_top;
    for (int i = 0; i < circuit_top; i++) {
        res.path[i] = circuit_stack[circuit_top - 1 - i];
    }
    free(circuit_stack);
    res.success = true;

    return res;
}
