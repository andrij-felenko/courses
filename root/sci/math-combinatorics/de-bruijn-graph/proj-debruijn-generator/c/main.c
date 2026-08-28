#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

/* Структура для опису орієнтованого графа де Брейнена */
typedef struct {
    uint32_t k;             /* Розмір алфавіту (наприклад, 2) */
    uint32_t n;             /* Розмір слова (наприклад, 3) */
    size_t num_nodes;       /* Кількість вершин = k^{n-1} */
    size_t num_edges;       /* Кількість ребер = k^n */
    uint32_t *adj_count;    /* Поточна кількість невідвіданих вихідних ребер */
} debruijn_graph_t;

/* Створення графа де Брейнена */
debruijn_graph_t* debruijn_create(uint32_t k, uint32_t n) {
    if (k < 2 || n < 1 || n > 20) return NULL;
    
    debruijn_graph_t *graph = (debruijn_graph_t*)malloc(sizeof(debruijn_graph_t));
    if (!graph) return NULL;

    graph->k = k;
    graph->n = n;
    
    size_t num_nodes = 1;
    for (uint32_t i = 0; i < n - 1; ++i) {
        num_nodes *= k;
    }
    
    graph->num_nodes = num_nodes;
    graph->num_edges = num_nodes * k;

    graph->adj_count = (uint32_t*)calloc(num_nodes, sizeof(uint32_t));
    if (!graph->adj_count) {
        free(graph);
        return NULL;
    }

    /* Кожна вершина спочатку має k невикористаних вихідних ребер */
    for (size_t i = 0; i < num_nodes; ++i) {
        graph->adj_count[i] = k;
    }

    return graph;
}

/* Звільнення пам'яті */
void debruijn_free(debruijn_graph_t *graph) {
    if (graph) {
        free(graph->adj_count);
        free(graph);
    }
}

/* Ітеративний алгоритм Гірхольцера для обходу Ейлерового циклу */
bool debruijn_generate(debruijn_graph_t *graph, uint8_t *output_seq) {
    if (!graph || !output_seq) return false;

    size_t num_edges = graph->num_edges;
    uint32_t k = graph->k;
    size_t mask = graph->num_nodes - 1; /* Маска для зсуву бітів при k=2 */

    /* Виділення динамічного стека для проходження */
    size_t *edge_stack = (size_t*)malloc((num_edges + 1) * sizeof(size_t));
    size_t *node_stack = (size_t*)malloc((num_edges + 1) * sizeof(size_t));
    if (!edge_stack || !node_stack) {
        free(edge_stack);
        free(node_stack);
        return false;
    }

    size_t stack_top = 0;
    size_t curr_node = 0; /* Стартуємо з вершини 0 (початковий префікс 00...0) */

    node_stack[stack_top] = curr_node;
    size_t out_idx = 0;

    while (stack_top > 0 || graph->adj_count[curr_node] > 0) {
        if (graph->adj_count[curr_node] == 0) {
            /* Застрягли — додаємо ребро до вихідної послідовності */
            output_seq[out_idx++] = (uint8_t)edge_stack[stack_top];
            curr_node = node_stack[--stack_top];
        } else {
            /* Вибираємо наступне невикористане ребро */
            graph->adj_count[curr_node]--;
            uint32_t symbol = graph->adj_count[curr_node];
            
            node_stack[++stack_top] = curr_node;
            edge_stack[stack_top] = symbol;

            /* Перехід до наступної вершини: лівий зсув та додавання символу */
            if (k == 2) {
                curr_node = ((curr_node << 1) | symbol) & mask;
            } else {
                curr_node = (curr_node * k + symbol) % graph->num_nodes;
            }
        }
    }

    free(edge_stack);
    free(node_stack);
    return true;
}

int main(void) {
    uint32_t k = 2, n = 3;
    debruijn_graph_t *g = debruijn_create(k, n);
    if (!g) return 1;

    size_t seq_len = g->num_edges;
    uint8_t *seq = (uint8_t*)malloc(seq_len * sizeof(uint8_t));

    if (debruijn_generate(g, seq)) {
        printf("Послідовність де Брейнена B(%u, %u) [довжина %zu]: ", k, n, seq_len);
        for (size_t i = 0; i < seq_len; ++i) {
            printf("%u", seq[i]);
        }
        printf("\n");
    }

    free(seq);
    debruijn_free(g);
    return 0;
}
