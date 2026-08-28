#include <stdio.h>
#include <stdint.h>
#include <size_t.h>

/* Обчислення плоского індексу ребра між вершинами u та v (u < v) */
size_t complete_graph_edge_id(size_t u, size_t v) {
    if (u > v) {
        size_t tmp = u;
        u = v;
        v = tmp;
    }
    if (u == v) return SIZE_MAX; // Немає петлі у простому графі
    
    return v * (v - 1) / 2 + u;
}

/* Відновлення пари вершин (u, v) за edge_id */
void complete_graph_inverse_edge_id(size_t edge_id, size_t *out_u, size_t *out_v) {
    uint64_t disc = 8 * (uint64_t)edge_id + 1;
    uint64_t s = 0;
    while ((s + 1) * (s + 1) <= disc) {
        s++;
    }
    
    size_t v = (size_t)(s - 1) / 2 + 1;
    size_t u = edge_id - v * (v - 1) / 2;
    
    if (out_u) *out_u = u;
    if (out_v) *out_v = v;
}
