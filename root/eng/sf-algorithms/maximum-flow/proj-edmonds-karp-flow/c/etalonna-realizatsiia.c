#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_NODES 5000
#define MAX_ARCS  60000
#define FLOW_INF  INT64_MAX

typedef struct {
    int to;
    int next;
    int64_t cap;
    int64_t flow;
} FlowArc;

typedef struct {
    int n;
    int arc_count;
    int head[MAX_NODES];
    FlowArc arcs[MAX_ARCS];
} FlowNetworkC;

void flow_network_init(FlowNetworkC* net, int n) {
    net->n = n;
    net->arc_count = 0;
    memset(net->head, -1, sizeof(int) * n);
}

void flow_network_add_edge(FlowNetworkC* net, int from, int to, int64_t cap, int64_t rev_cap) {
    if (from == to || from < 0 || to < 0 || from >= net->n || to >= net->n) return;

    // Пряме ребро з парним індексом 2k
    net->arcs[net->arc_count] = (FlowArc){to, net->head[from], cap, 0};
    net->head[from] = net->arc_count++;

    // Зворотне ребро з непарним індексом 2k + 1
    net->arcs[net->arc_count] = (FlowArc){from, net->head[to], rev_cap, 0};
    net->head[to] = net->arc_count++;
}

static bool flow_network_bfs(FlowNetworkC* net, int s, int t, int parent_edge[MAX_NODES]) {
    memset(parent_edge, -1, sizeof(int) * net->n);
    int queue[MAX_NODES];
    int q_head = 0, q_tail = 0;

    queue[q_tail++] = s;
    parent_edge[s] = -2; // Спеціальна позначка для джерела

    while (q_head < q_tail) {
        int u = queue[q_head++];
        if (u == t) return true;

        for (int e = net->head[u]; e != -1; e = net->arcs[e].next) {
            int v = net->arcs[e].to;
            int64_t res_cap = net->arcs[e].cap - net->arcs[e].flow;

            if (res_cap > 0 && parent_edge[v] == -1) {
                parent_edge[v] = e;
                queue[q_tail++] = v;
            }
        }
    }

    return parent_edge[t] != -1;
}

int64_t flow_network_max_flow(FlowNetworkC* net, int s, int t) {
    if (s == t) return 0;
    int64_t total_flow = 0;
    int parent_edge[MAX_NODES];

    while (flow_network_bfs(net, s, t, parent_edge)) {
        int64_t push_delta = FLOW_INF;

        // 1. Пошук вузького місця
        for (int curr = t; curr != s; ) {
            int e = parent_edge[curr];
            int64_t res_cap = net->arcs[e].cap - net->arcs[e].flow;
            if (res_cap < push_delta) push_delta = res_cap;
            curr = net->arcs[e ^ 1].to; // Повернення назад до батька через реверсивне ребро
        }

        // 2. Аугментація потоку
        for (int curr = t; curr != s; ) {
            int e = parent_edge[curr];
            net->arcs[e].flow += push_delta;
            net->arcs[e ^ 1].flow -= push_delta;
            curr = net->arcs[e ^ 1].to;
        }

        total_flow += push_delta;
    }

    return total_flow;
}

void flow_network_min_cut(FlowNetworkC* net, int s, bool in_s[MAX_NODES]) {
    memset(in_s, false, sizeof(bool) * net->n);
    int queue[MAX_NODES];
    int q_head = 0, q_tail = 0;

    queue[q_tail++] = s;
    in_s[s] = true;

    while (q_head < q_tail) {
        int u = queue[q_head++];
        for (int e = net->head[u]; e != -1; e = net->arcs[e].next) {
            int v = net->arcs[e].to;
            if (net->arcs[e].cap - net->arcs[e].flow > 0 && !in_s[v]) {
                in_s[v] = true;
                queue[q_tail++] = v;
            }
        }
    }
}
