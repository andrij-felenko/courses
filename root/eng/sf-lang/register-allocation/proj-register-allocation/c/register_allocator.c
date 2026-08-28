/* register_allocator.c — Реалізація алокатора регістрів мовою C (ANSI C / C99) */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_NODES 64
#define NO_COLOR -1
#define SPILL_COLOR -2

typedef struct {
    int id;
    int start;
    int end;
    double spill_cost;
    bool is_precolored;
} LiveInterval;

typedef struct {
    int num_nodes;
    int num_colors; // K фізичних регістрів
    LiveInterval intervals[MAX_NODES];
    bool adj[MAX_NODES][MAX_NODES];
    int degree[MAX_NODES];
    int colors[MAX_NODES];
    bool removed[MAX_NODES];
} InterferenceGraph;

/* Ініціалізація графа інтерференції */
void graph_init(InterferenceGraph *g, int num_colors) {
    g->num_nodes = 0;
    g->num_colors = num_colors;
    for (int i = 0; i < MAX_NODES; i++) {
        g->degree[i] = 0;
        g->colors[i] = NO_COLOR;
        g->removed[i] = false;
        for (int j = 0; j < MAX_NODES; j++) {
            g->adj[i][j] = false;
        }
    }
}

/* Додавання віртуальної змінної */
int graph_add_node(InterferenceGraph *g, int id, int start, int end, double cost, bool precolored) {
    int idx = g->num_nodes++;
    g->intervals[idx].id = id;
    g->intervals[idx].start = start;
    g->intervals[idx].end = end;
    g->intervals[idx].spill_cost = cost;
    g->intervals[idx].is_precolored = precolored;
    return idx;
}

/* Перевірка перетину піввідкритих інтервалів життєвості [start, end) */
static bool intervals_overlap(const LiveInterval *a, const LiveInterval *b) {
    return !(a->end <= b->start || b->end <= a->start);
}

/* Побудова ребер графа інтерференції */
void graph_build_edges(InterferenceGraph *g) {
    for (int i = 0; i < g->num_nodes; i++) {
        for (int j = i + 1; j < g->num_nodes; j++) {
            if (intervals_overlap(&g->intervals[i], &g->intervals[j])) {
                g->adj[i][j] = true;
                g->adj[j][i] = true;
                g->degree[i]++;
                g->degree[j]++;
            }
        }
    }
}

/* Запуск алгоритму розфарбування Чейтіна-Бріґґса */
bool graph_allocate_registers(InterferenceGraph *g) {
    int stack[MAX_NODES];
    int stack_top = 0;
    int remaining = g->num_nodes;

    /* Фаза 1: Спрощення (Simplify & Spill) */
    while (remaining > 0) {
        int candidate = -1;

        /* Шукаємо вершину з deg < K (Правило Кемпе), яка не є precolored */
        for (int i = 0; i < g->num_nodes; i++) {
            if (!g->removed[i] && !g->intervals[i].is_precolored && g->degree[i] < g->num_colors) {
                candidate = i;
                break;
            }
        }

        /* Якщо всі вершини мають deg >= K, обираємо кандидат на Spill за мінімальним пріоритетом */
        if (candidate == -1) {
            double min_priority = 1e9;
            for (int i = 0; i < g->num_nodes; i++) {
                if (!g->removed[i] && !g->intervals[i].is_precolored) {
                    double priority = g->intervals[i].spill_cost / (double)(g->degree[i] + 1);
                    if (priority < min_priority) {
                        min_priority = priority;
                        candidate = i;
                    }
                }
            }
        }

        if (candidate == -1) break; // Залишилися лише precolored вершини

        /* Вилучаємо обрану вершину і додаємо у стек */
        g->removed[candidate] = true;
        stack[stack_top++] = candidate;
        remaining--;

        /* Оновлюємо степені сусідів */
        for (int i = 0; i < g->num_nodes; i++) {
            if (g->adj[candidate][i] && !g->removed[i]) {
                g->degree[i]--;
            }
        }
    }

    /* Фаза 2: Вибір кольорів (Select & Optimistic Coloring) */
    bool has_spills = false;
    while (stack_top > 0) {
        int node = stack[--stack_top];
        g->removed[node] = false;

        /* Визначаємо зайняті кольори сусідів */
        bool used_colors[MAX_NODES] = { false };
        for (int i = 0; i < g->num_nodes; i++) {
            if (g->adj[node][i] && !g->removed[i] && g->colors[i] >= 0) {
                used_colors[g->colors[i]] = true;
            }
        }

        /* Шукаємо перший вільний колір з K доступних */
        int assigned_color = NO_COLOR;
        for (int c = 0; c < g->num_colors; c++) {
            if (!used_colors[c]) {
                assigned_color = c;
                break;
            }
        }

        if (assigned_color != NO_COLOR) {
            g->colors[node] = assigned_color;
        } else {
            /* Оптимістичне розфарбування не вдалося -> Фактичний Spill */
            g->colors[node] = SPILL_COLOR;
            has_spills = true;
        }
    }

    return !has_spills;
}

int main(void) {
    InterferenceGraph g;
    graph_init(&g, 3); // K = 3 фізичні регістри (R0, R1, R2)

    /* Додаємо 5 віртуальних змінних */
    graph_add_node(&g, 1, 1, 3, 10.0, false); // v1
    graph_add_node(&g, 2, 2, 4, 15.0, false); // v2
    graph_add_node(&g, 3, 1, 5, 25.0, false); // v3
    graph_add_node(&g, 4, 4, 5, 5.0, false);  // v4
    graph_add_node(&g, 5, 3, 5, 12.0, false); // v5

    graph_build_edges(&g);
    bool success = graph_allocate_registers(&g);

    printf("=== Результат розподілу регістрів (C Implementation) ===\n");
    printf("Успішність розподілу без Spill: %s\n", success ? "ТАК" : "НІ");
    for (int i = 0; i < g.num_nodes; i++) {
        if (g.colors[i] >= 0) {
            printf("Змінна v%d -> Регістр R%d\n", g.intervals[i].id, g.colors[i]);
        } else {
            printf("Змінна v%d -> SPILL у стек пам'яті [rsp + %d]\n", g.intervals[i].id, i * 8);
        }
    }
    return 0;
}
