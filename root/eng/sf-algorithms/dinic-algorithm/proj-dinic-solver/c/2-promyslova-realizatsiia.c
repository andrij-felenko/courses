#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_VERTICES 10000
#define MAX_EDGES 200000
#define INF_FLOW INT64_MAX

typedef struct {
    int to;
    int next;
    int64_t cap;
    int64_t flow;
} DinicEdge;

typedef struct {
    int n;
    int edge_count;
    int head[MAX_VERTICES];
    int level[MAX_VERTICES];
    int ptr[MAX_VERTICES];
    int queue[MAX_VERTICES];
    DinicEdge edges[MAX_EDGES];
} DinicC;

void dinic_init(DinicC* g, int n) {
    g->n = n;
    g->edge_count = 0;
    memset(g->head, -1, sizeof(int) * n);
}

void dinic_add_edge(DinicC* g, int from, int to, int64_t cap, int64_t rev_cap) {
    if (from == to) return;
    
    // Пряме ребро (парний індекс 2k)
    g->edges[g->edge_count] = (DinicEdge){to, g->head[from], cap, 0};
    g->head[from] = g->edge_count++;

    // Зворотне ребро (непарний індекс 2k + 1)
    g->edges[g->edge_count] = (DinicEdge){from, g->head[to], rev_cap, 0};
    g->head[to] = g->edge_count++;
}

static bool dinic_bfs(DinicC* g, int s, int t) {
    memset(g->level, -1, sizeof(int) * g->n);
    int qhead = 0, qtail = 0;
    
    g->level[s] = 0;
    g->queue[qtail++] = s;

    while (qhead < qtail) {
        int u = g->queue[qhead++];
        for (int e = g->head[u]; e != -1; e = g->edges[e].next) {
            int v = g->edges[e].to;
            if (g->edges[e].cap - g->edges[e].flow > 0 && g->level[v] == -1) {
                g->level[v] = g->level[u] + 1;
                g->queue[qtail++] = v;
            }
        }
    }
    return g->level[t] != -1;
}

static int64_t dinic_dfs(DinicC* g, int u, int t, int64_t pushed) {
    if (pushed == 0 || u == t) return pushed;

    for (int* e = &g->ptr[u]; *e != -1; *e = g->edges[*e].next) {
        int edge_idx = *e;
        int v = g->edges[edge_idx].to;
        int64_t res = g->edges[edge_idx].cap - g->edges[edge_idx].flow;

        if (g->level[u] + 1 != g->level[v] || res == 0) continue;

        int64_t push_next = pushed < res ? pushed : res;
        int64_t tr = dinic_dfs(g, v, t, push_next);
        if (tr == 0) continue;

        g->edges[edge_idx].flow += tr;
        g->edges[edge_idx ^ 1].flow -= tr; // XOR trick для зворотного ребра
        return tr;
    }
    return 0;
}

int64_t dinic_max_flow(DinicC* g, int s, int t) {
    int64_t total_flow = 0;
    while (dinic_bfs(g, s, t)) {
        memcpy(g->ptr, g->head, sizeof(int) * g->n);
        while (1) {
            int64_t pushed = dinic_dfs(g, s, t, INF_FLOW);
            if (pushed == 0) break;
            total_flow += pushed;
        }
    }
    return total_flow;
}
