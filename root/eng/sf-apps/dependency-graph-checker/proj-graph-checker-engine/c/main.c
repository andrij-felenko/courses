#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_NODES 128
#define MAX_NAME 64

typedef struct {
    char name[MAX_NAME];
    int layer;         /* Індекс шару: 0 - Infra, 1 - Domain, 2 - App, 3 - Presentation */
    int context_id;    /* Ідентифікатор обмеженого контексту (Bounded Context) */
} NodeMeta;

typedef struct {
    int to;
    int next;
} Edge;

typedef struct {
    NodeMeta nodes[MAX_NODES];
    int head[MAX_NODES];
    Edge edges[MAX_NODES * MAX_NODES];
    int node_count;
    int edge_count;
} Graph;

/* Ініціалізація графа */
void graph_init(Graph *g) {
    g->node_count = 0;
    g->edge_count = 0;
    for (int i = 0; i < MAX_NODES; ++i) {
        g->head[i] = -1;
    }
}

/* Додавання або отримання існуючого вузла за унікальним іменем */
int graph_add_node(Graph *g, const char *name, int layer, int context_id) {
    for (int i = 0; i < g->node_count; ++i) {
        if (strcmp(g->nodes[i].name, name) == 0) {
            return i;
        }
    }
    if (g->node_count >= MAX_NODES) {
        fprintf(stderr, "Помилка: перевищено ліміт вузлів (%d)\n", MAX_NODES);
        exit(1);
    }
    int id = g->node_count++;
    strncpy(g->nodes[id].name, name, MAX_NAME - 1);
    g->nodes[id].name[MAX_NAME - 1] = '\0';
    g->nodes[id].layer = layer;
    g->nodes[id].context_id = context_id;
    return id;
}

/* Додавання орієнтованого ребра залежності from -> to */
void graph_add_edge(Graph *g, int from, int to) {
    int e = g->edge_count++;
    g->edges[e].to = to;
    g->edges[e].next = g->head[from];
    g->head[from] = e;
}

/* Стан виконання алгоритму Тар'яна */
typedef struct {
    int dfn[MAX_NODES];
    int low[MAX_NODES];
    bool in_stack[MAX_NODES];
    int stack[MAX_NODES];
    int top;
    int timer;
    int cycle_count;
} TarjanState;

static int min_val(int a, int b) {
    return a < b ? a : b;
}

static void tarjan_dfs(Graph *g, TarjanState *st, int u) {
    st->dfn[u] = st->low[u] = ++st->timer;
    st->stack[++st->top] = u;
    st->in_stack[u] = true;

    for (int e = g->head[u]; e != -1; e = g->edges[e].next) {
        int v = g->edges[e].to;
        if (st->dfn[v] == 0) {
            /* Пряме ребро дерева пошуку (Tree Edge) */
            tarjan_dfs(g, st, v);
            st->low[u] = min_val(st->low[u], st->low[v]);
        } else if (st->in_stack[v]) {
            /* Зворотне ребро до предка в поточному стеку (Back Edge) */
            st->low[u] = min_val(st->low[u], st->dfn[v]);
        }
    }

    /* Якщо знайдено корінь сильно зв'язаної компоненти */
    if (st->low[u] == st->dfn[u]) {
        int scc_members[MAX_NODES];
        int count = 0;
        while (st->top >= 0) {
            int node = st->stack[st->top--];
            st->in_stack[node] = false;
            scc_members[count++] = node;
            if (node == u) break;
        }

        /* Якщо в компоненті більше 1 вузла — це циклічна ерозія */
        if (count > 1) {
            st->cycle_count++;
            printf("[ПОМИЛКА: ЦИКЛ #%d] Сильно зв'язана компонента (%d вузлів):\n  ", 
                   st->cycle_count, count);
            for (int i = 0; i < count; ++i) {
                printf("%s%s", g->nodes[scc_members[i]].name, 
                       (i + 1 < count) ? " <-> " : "\n");
            }
        }
    }
}

/* Пошук усіх циклів у графі */
int check_cycles(Graph *g) {
    TarjanState st;
    memset(&st, 0, sizeof(TarjanState));

    for (int i = 0; i < g->node_count; ++i) {
        if (st.dfn[i] == 0) {
            tarjan_dfs(g, &st, i);
        }
    }
    return st.cycle_count;
}

/* Перевірка шарових обмежень: вищий шар не може залежати від вищого за себе */
int check_layer_violations(Graph *g) {
    int violations = 0;
    for (int u = 0; u < g->node_count; ++u) {
        for (int e = g->head[u]; e != -1; e = g->edges[e].next) {
            int v = g->edges[e].to;
            /* Правило: шар u не може залежати від v, якщо layer(u) < layer(v) (зворотний виклик) */
            if (g->nodes[u].layer < g->nodes[v].layer) {
                violations++;
                printf("[ПОМИЛКА: ШАР] Зворотна залежність: %s (шар %d) -> %s (шар %d)\n",
                       g->nodes[u].name, g->nodes[u].layer,
                       g->nodes[v].name, g->nodes[v].layer);
            }
        }
    }
    return violations;
}

int main(void) {
    Graph g;
    graph_init(&g);

    /* Створення вузлів системи (Layer: 0-Infra, 1-Domain, 2-App, 3-Presentation) */
    int api   = graph_add_node(&g, "Presentation.HttpApi", 3, 1);
    int order = graph_add_node(&g, "Application.OrderService", 2, 1);
    int core  = graph_add_node(&g, "Domain.OrderCore", 1, 1);
    int repo  = graph_add_node(&g, "Infrastructure.PostgresRepo", 0, 1);
    int bill  = graph_add_node(&g, "Application.BillingService", 2, 2);

    /* Дозволені залежності */
    graph_add_edge(&g, api, order);
    graph_add_edge(&g, order, core);
    graph_add_edge(&g, order, repo);

    /* Порушення 1: Зворотна залежність Domain -> Infrastructure (DIP) */
    graph_add_edge(&g, core, repo);

    /* Порушення 2: Цикл між сервісами OrderService <-> BillingService */
    graph_add_edge(&g, order, bill);
    graph_add_edge(&g, bill, order);

    printf("=== СТАТИЧНИЙ АНАЛІЗ АРХІТЕКТУРНИХ ЗАЛЕЖНОСТЕЙ (C) ===\n");
    int cycles = check_cycles(&g);
    int layer_errs = check_layer_violations(&g);

    printf("\nПідсумок: виявлено %d циклів та %d шарових порушень.\n", cycles, layer_errs);
    return (cycles + layer_errs > 0) ? 1 : 0;
}
