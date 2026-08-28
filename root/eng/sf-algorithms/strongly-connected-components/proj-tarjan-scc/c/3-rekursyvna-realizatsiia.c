#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MIN(a, b) ((a) < (b) ? (a) : (b))

typedef struct EdgeNode {
    int to;
    struct EdgeNode* next;
} EdgeNode;

typedef struct {
    int num_vertices;
    EdgeNode** adj;
} Graph;

Graph* graph_create(int vertices) {
    Graph* g = (Graph*)malloc(sizeof(Graph));
    g->num_vertices = vertices;
    g->adj = (EdgeNode**)calloc(vertices, sizeof(EdgeNode*));
    return g;
}

void graph_add_edge(Graph* g, int u, int v) {
    EdgeNode* node = (EdgeNode*)malloc(sizeof(EdgeNode));
    node->to = v;
    node->next = g->adj[u];
    g->adj[u] = node;
}

void graph_free(Graph* g) {
    for (int i = 0; i < g->num_vertices; i++) {
        EdgeNode* curr = g->adj[i];
        while (curr) {
            EdgeNode* tmp = curr;
            curr = curr->next;
            free(tmp);
        }
    }
    free(g->adj);
    free(g);
}

typedef struct {
    int timer;
    int stack_top;
    int* tin;
    int* low;
    int* stack;
    bool* in_stack;
    int scc_count;
} TarjanContext;

static void tarjan_dfs(int u, const Graph* g, TarjanContext* ctx) {
    ctx->tin[u] = ctx->low[u] = ++(ctx->timer);
    ctx->stack[++(ctx->stack_top)] = u;
    ctx->in_stack[u] = true;

    for (EdgeNode* edge = g->adj[u]; edge != NULL; edge = edge->next) {
        int v = edge->to;
        if (ctx->tin[v] == 0) {
            tarjan_dfs(v, g, ctx);
            ctx->low[u] = MIN(ctx->low[u], ctx->low[v]);
        } else if (ctx->in_stack[v]) {
            ctx->low[u] = MIN(ctx->low[u], ctx->tin[v]);
        }
    }

    if (ctx->low[u] == ctx->tin[u]) {
        ctx->scc_count++;
        printf("SCC #%d: [ ", ctx->scc_count);
        while (1) {
            int v = ctx->stack[(ctx->stack_top)--];
            ctx->in_stack[v] = false;
            printf("%d ", v);
            if (u == v) break;
        }
        printf("]\n");
    }
}

void find_scc_recursive(const Graph* g) {
    int v_count = g->num_vertices;
    TarjanContext ctx;
    ctx.timer = 0;
    ctx.stack_top = -1;
    ctx.scc_count = 0;

    ctx.tin = (int*)calloc(v_count, sizeof(int));
    ctx.low = (int*)calloc(v_count, sizeof(int));
    ctx.stack = (int*)malloc(v_count * sizeof(int));
    ctx.in_stack = (bool*)calloc(v_count, sizeof(bool));

    for (int i = 0; i < v_count; i++) {
        if (ctx.tin[i] == 0) {
            tarjan_dfs(i, g, &ctx);
        }
    }

    free(ctx.tin);
    free(ctx.low);
    free(ctx.stack);
    free(ctx.in_stack);
}
