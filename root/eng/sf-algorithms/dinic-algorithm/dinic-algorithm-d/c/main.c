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
} CDinicEdge;

typedef struct {
    int n;
    int edge_count;
    int head[MAX_VERTICES];
    int level[MAX_VERTICES];
    int ptr[MAX_VERTICES];
    int queue[MAX_VERTICES];
    CDinicEdge edges[MAX_EDGES];
} CDinic;

void c_dinic_init(CDinic* g, int n) {
    g->n = n;
    g->edge_count = 0;
    memset(g->head, -1, sizeof(int) * n);
}

void c_dinic_add_edge(CDinic* g, int from, int to, int64_t cap, int64_t rev_cap) {
    if (from == to) return;
    g->edges[g->edge_count] = (CDinicEdge){to, g->head[from], cap, 0};
    g->head[from] = g->edge_count++;
    g->edges[g->edge_count] = (CDinicEdge){from, g->head[to], rev_cap, 0};
    g->head[to] = g->edge_count++;
}

static bool c_dinic_bfs(CDinic* g, int s, int t) {
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

static int64_t c_dinic_dfs(CDinic* g, int u, int t, int64_t pushed) {
    if (pushed == 0 || u == t) return pushed;

    for (int* e = &g->ptr[u]; *e != -1; *e = g->edges[*e].next) {
        int edge_idx = *e;
        int v = g->edges[edge_idx].to;
        int64_t res = g->edges[edge_idx].cap - g->edges[edge_idx].flow;

        if (g->level[u] + 1 != g->level[v] || res == 0) continue;

        int64_t push_next = pushed < res ? pushed : res;
        int64_t tr = c_dinic_dfs(g, v, t, push_next);
        if (tr == 0) continue;

        g->edges[edge_idx].flow += tr;
        g->edges[edge_idx ^ 1].flow -= tr;
        return tr;
    }
    return 0;
}

int64_t c_dinic_max_flow(CDinic* g, int s, int t) {
    int64_t total_flow = 0;
    while (c_dinic_bfs(g, s, t)) {
        memcpy(g->ptr, g->head, sizeof(int) * g->n);
        while (1) {
            int64_t pushed = c_dinic_dfs(g, s, t, INF_FLOW);
            if (pushed == 0) break;
            total_flow += pushed;
        }
    }
    return total_flow;
}
