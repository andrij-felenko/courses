/* complexity_evaluator.c - Метрики складності архітектурного графа на C */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NODES 64
#define MAX_NAME 64

typedef struct {
    char name[MAX_NAME];
    int call_targets[MAX_NODES];
    int target_count;
    bool is_pass_through; // Чи є модуль лише перенаправлячем
} ModuleNode;

typedef struct {
    ModuleNode nodes[MAX_NODES];
    int node_count;
} CallGraph;

void graph_init(CallGraph *g) {
    g->node_count = 0;
}

int graph_add_node(CallGraph *g, const char *name, bool is_pass_through) {
    if (g->node_count >= MAX_NODES) return -1;
    int id = g->node_count++;
    strncpy(g->nodes[id].name, name, MAX_NAME - 1);
    g->nodes[id].name[MAX_NAME - 1] = '\0';
    g->nodes[id].target_count = 0;
    g->nodes[id].is_pass_through = is_pass_through;
    return id;
}

void graph_add_edge(CallGraph *g, int src, int dst) {
    if (src >= 0 && src < g->node_count && dst >= 0 && dst < g->node_count) {
        g->nodes[src].call_targets[g->nodes[src].target_count++] = dst;
    }
}

static int dfs_max_depth(const CallGraph *g, int current, bool visited[]) {
    visited[current] = true;
    int max_sub_depth = 0;
    
    for (int i = 0; i < g->nodes[current].target_count; ++i) {
        int target = g->nodes[current].call_targets[i];
        if (!visited[target]) {
            int d = dfs_max_depth(g, target, visited);
            if (d > max_sub_depth) max_sub_depth = d;
        }
    }
    visited[current] = false;
    return 1 + max_sub_depth;
}

void evaluate_architectural_taste(const CallGraph *g) {
    int max_depth = 0;
    int pass_through_count = 0;
    bool visited[MAX_NODES] = { false };

    for (int i = 0; i < g->node_count; ++i) {
        if (g->nodes[i].is_pass_through) {
            pass_through_count++;
        }
        int d = dfs_max_depth(g, i, visited);
        if (d > max_depth) max_depth = d;
    }

    double wrapper_ratio = (double)pass_through_count / (g->node_count > 0 ? g->node_count : 1);

    printf("=== ARCHITECTURAL TASTE METRICS REPORT (C) ===\n");
    printf("Total Modules Registered : %d\n", g->node_count);
    printf("Max Indirection Depth    : %d (Threshold: <= 5)\n", max_depth);
    printf("Wrapper Module Ratio     : %.2f (Threshold: <= 0.30)\n", wrapper_ratio);

    if (max_depth > 5 || wrapper_ratio > 0.30) {
        printf("RESULT: [WARNING] Over-engineering detected! System lacks taste simplicity.\n");
    } else {
        printf("RESULT: [OK] Architectural taste budget is respected.\n");
    }
}

int main(void) {
    CallGraph g;
    graph_init(&g);

    // Приклад надпроектованого ланцюжка
    int n0 = graph_add_node(&g, "HTTPController", true);
    int n1 = graph_add_node(&g, "RequestValidatorAdapter", true);
    int n2 = graph_add_node(&g, "DeviceCommandService", true);
    int n3 = graph_add_node(&g, "AccessControlMediator", true);
    int n4 = graph_add_node(&g, "GenericRuleEngineFactory", true);
    int n5 = graph_add_node(&g, "LockHardwareExecutor", false);

    graph_add_edge(&g, n0, n1);
    graph_add_edge(&g, n1, n2);
    graph_add_edge(&g, n2, n3);
    graph_add_edge(&g, n3, n4);
    graph_add_edge(&g, n4, n5);

    evaluate_architectural_taste(&g);
    return 0;
}
