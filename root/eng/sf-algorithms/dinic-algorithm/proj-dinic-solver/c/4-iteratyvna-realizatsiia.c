#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_V 10000
#define MAX_E 200000
#define INF_64 INT64_MAX

typedef struct {
    int to;
    int next;
    int64_t cap;
    int64_t flow;
} IterEdge;

typedef struct {
    int n;
    int edge_count;
    int head[MAX_V];
    int level[MAX_V];
    int ptr[MAX_V];
    int queue[MAX_V];
    int path[MAX_V];
    IterEdge edges[MAX_E];
} IterDinicC;

void iter_dinic_init(IterDinicC* g, int n) {
    g->n = n;
    g->edge_count = 0;
    memset(g->head, -1, sizeof(int) * n);
}

void iter_dinic_add_edge(IterDinicC* g, int u, int v, int64_t cap) {
    if (u == v) return;
    g->edges[g->edge_count] = (IterEdge){v, g->head[u], cap, 0};
    g->head[u] = g->edge_count++;
    g->edges[g->edge_count] = (IterEdge){u, g->head[v], 0, 0};
    g->head[v] = g->edge_count++;
}

static bool iter_bfs(IterDinicC* g, int s, int t) {
    memset(g->level, -1, sizeof(int) * g->n);
    int qh = 0, qt = 0;
    g->level[s] = 0;
    g->queue[qt++] = s;

    while (qh < qt) {
        int u = g->queue[qh++];
        for (int e = g->head[u]; e != -1; e = g->edges[e].next) {
            int v = g->edges[e].to;
            if (g->edges[e].cap - g->edges[e].flow > 0 && g->level[v] == -1) {
                g->level[v] = g->level[u] + 1;
                g->queue[qt++] = v;
            }
        }
    }
    return g->level[t] != -1;
}

static int64_t iter_push_blocking(IterDinicC* g, int s, int t) {
    int64_t phase_flow = 0;
    int path_len = 0;
    g->path[path_len++] = s;

    while (path_len > 0) {
        int u = g->path[path_len - 1];

        if (u == t) {
            int64_t pushed = INF_64;
            int bottleneck = -1;

            for (int i = 0; i < path_len - 1; ++i) {
                int curr = g->path[i];
                int e = g->ptr[curr];
                int64_t res = g->edges[e].cap - g->edges[e].flow;
                if (res < pushed) {
                    pushed = res;
                    bottleneck = i;
                }
            }

            for (int i = 0; i < path_len - 1; ++i) {
                int curr = g->path[i];
                int e = g->ptr[curr];
                g->edges[e].flow += pushed;
                g->edges[e ^ 1].flow -= pushed;
            }

            phase_flow += pushed;
            path_len = bottleneck + 1;
            continue;
        }

        bool adv = false;
        while (g->ptr[u] != -1) {
            int e = g->ptr[u];
            int v = g->edges[e].to;
            if (g->level[u] + 1 == g->level[v] && g->edges[e].cap - g->edges[e].flow > 0) {
                g->path[path_len++] = v;
                adv = true;
                break;
            }
            g->ptr[u] = g->edges[e].next;
        }

        if (!adv) {
            --path_len;
            if (path_len > 0) {
                int prev = g->path[path_len - 1];
                g->ptr[prev] = g->edges[g->ptr[prev]].next;
            }
        }
    }
    return phase_flow;
}

int64_t iter_dinic_max_flow(IterDinicC* g, int s, int t) {
    int64_t total = 0;
    while (iter_bfs(g, s, t)) {
        memcpy(g->ptr, g->head, sizeof(int) * g->n);
        total += iter_push_blocking(g, s, t);
    }
    return total;
}
