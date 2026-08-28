#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_NODES 16
#define MAX_EDGES 32
#define MAX_RESOURCES 4
#define MAX_II 32
#define MAX_BUDGET 64

// Типи апаратних функціональних блоків процесора
typedef enum {
    RES_MEM = 0, // Порти пам'яті (Load / Store)
    RES_ALU = 1, // Цілочислові АЛП (Add, Sub, Logic)
    RES_MUL = 2, // Блоки конвеєрного множення (Mul)
    RES_COUNT
} ResourceType;

// Ребро залежності між операціями в графі DDG
typedef struct {
    int src;          // Індекс операції-джерела
    int dst;          // Індекс операції-споживача
    int latency;      // Латентність d(u, v) у тактах
    int distance;     // Дистанція за ітераціями delta(u, v)
} Edge;

// Вузол графа залежностей (окрема машинна операція)
typedef struct {
    const char *name;     // Символьна назва операції
    ResourceType res;     // Необхідний функціональний блок
    int latency;          // Власна тривалість операції
    int height;           // Пріоритет висоти в графі
    int sched_time;       // Запланований абсолютний такт (-1, якщо не заплановано)
    int budget;           // Лічильник спроб для запобігання зацикленню відкатів
} Node;

// Граф залежностей за даними
typedef struct {
    Node nodes[MAX_NODES];
    Edge edges[MAX_EDGES];
    int node_count;
    int edge_count;
    int res_units[RES_COUNT]; // Кількість фізичних пристроїв кожного типу
} Graph;

// Таблиця модульного резервування (MRT)
typedef struct {
    int ii;
    int table[MAX_II][MAX_RESOURCES]; // table[slot][res_type] = кількість зайнятих блоків
    int occupied_by[MAX_II][MAX_RESOURCES][MAX_NODES]; // Індекси призначених операцій
} MRT;

// Ініціалізація таблиці MRT для заданого значення II
static void mrt_init(MRT *mrt, int ii) {
    mrt->ii = ii;
    memset(mrt->table, 0, sizeof(mrt->table));
    for (int s = 0; s < MAX_II; ++s) {
        for (int r = 0; r < MAX_RESOURCES; ++r) {
            for (int n = 0; n < MAX_NODES; ++n) {
                mrt->occupied_by[s][r][n] = -1;
            }
        }
    }
}

// Перевірка доступності ресурсу в слоті (time mod II)
static bool mrt_can_reserve(const MRT *mrt, const Graph *g, ResourceType res, int time) {
    int slot = time % mrt->ii;
    return mrt->table[slot][res] < g->res_units[res];
}

// Резервування ресурсу в таблиці MRT
static void mrt_reserve(MRT *mrt, int node_id, ResourceType res, int time) {
    int slot = time % mrt->ii;
    int count = mrt->table[slot][res];
    mrt->occupied_by[slot][res][count] = node_id;
    mrt->table[slot][res]++;
}

// Звільнення ресурсу в MRT при витісненні операції під час відкату
static void mrt_unreserve(MRT *mrt, int node_id, ResourceType res, int time) {
    int slot = time % mrt->ii;
    int count = mrt->table[slot][res];
    for (int i = 0; i < count; ++i) {
        if (mrt->occupied_by[slot][res][i] == node_id) {
            for (int j = i; j < count - 1; ++j) {
                mrt->occupied_by[slot][res][j] = mrt->occupied_by[slot][res][j + 1];
            }
            mrt->occupied_by[slot][res][count - 1] = -1;
            mrt->table[slot][res]--;
            break;
        }
    }
}

// Обчислення ресурсного бар'єра ResMII
static int compute_res_mii(const Graph *g) {
    int res_mii = 1;
    for (int r = 0; r < RES_COUNT; ++r) {
        int count = 0;
        for (int i = 0; i < g->node_count; ++i) {
            if (g->nodes[i].res == r) count++;
        }
        int units = g->res_units[r] > 0 ? g->res_units[r] : 1;
        int mii_r = (count + units - 1) / units;
        if (mii_r > res_mii) res_mii = mii_r;
    }
    return res_mii;
}

// Обчислення рекурентного бар'єра RecMII для циклічних залежностей
static int compute_rec_mii(const Graph *g) {
    int rec_mii = 1;
    for (int e = 0; e < g->edge_count; ++e) {
        if (g->edges[e].src == g->edges[e].dst && g->edges[e].distance > 0) {
            int ratio = (g->edges[e].latency + g->edges[e].distance - 1) / g->edges[e].distance;
            if (ratio > rec_mii) rec_mii = ratio;
        }
    }
    return rec_mii;
}

// Розрахунок пріоритетів висоти (Height) у графі DDG
static void compute_heights(Graph *g, int mii) {
    for (int i = 0; i < g->node_count; ++i) {
        g->nodes[i].height = g->nodes[i].latency;
    }
    bool changed = true;
    while (changed) {
        changed = false;
        for (int e = 0; e < g->edge_count; ++e) {
            int u = g->edges[e].src;
            int v = g->edges[e].dst;
            int d = g->edges[e].latency;
            int delta = g->edges[e].distance;
            int eff_d = d - delta * mii;
            if (g->nodes[u].height < g->nodes[v].height + eff_d) {
                g->nodes[u].height = g->nodes[v].height + eff_d;
                changed = true;
            }
        }
    }
}

// Обчислення раннього моменту старту EStart на основі запланованих предків
static int compute_estart(const Graph *g, int node_id, int ii) {
    int estart = 0;
    for (int e = 0; e < g->edge_count; ++e) {
        if (g->edges[e].dst == node_id) {
            int p = g->edges[e].src;
            if (g->nodes[p].sched_time != -1) {
                int min_t = g->nodes[p].sched_time + g->edges[e].latency - g->edges[e].distance * ii;
                if (min_t > estart) estart = min_t;
            }
        }
    }
    return estart;
}

// Головний цикл планування Iterative Modulo Scheduling (IMS)
static bool ims_schedule(Graph *g, int *final_ii, int *final_length) {
    int res_mii = compute_res_mii(g);
    int rec_mii = compute_rec_mii(g);
    int ii = (res_mii > rec_mii) ? res_mii : rec_mii;

    printf("Розрахункові бар'єри: ResMII = %d, RecMII = %d -> Старт із II = %d\n", res_mii, rec_mii, ii);

    while (ii <= MAX_II) {
        MRT mrt;
        mrt_init(&mrt, ii);
        compute_heights(g, ii);

        for (int i = 0; i < g->node_count; ++i) {
            g->nodes[i].sched_time = -1;
            g->nodes[i].budget = MAX_BUDGET;
        }

        bool success = true;
        int unscheduled_count = g->node_count;

        while (unscheduled_count > 0) {
            // Вибір нерозкладеної вершини з найвищим пріоритетом Height
            int best_node = -1;
            int max_height = -9999;
            for (int i = 0; i < g->node_count; ++i) {
                if (g->nodes[i].sched_time == -1 && g->nodes[i].height > max_height) {
                    max_height = g->nodes[i].height;
                    best_node = i;
                }
            }

            if (best_node == -1) break;

            if (g->nodes[best_node].budget <= 0) {
                printf("Бюджет спроб для операції '%s' вичерпано. Збільшуємо II = %d -> %d\n",
                       g->nodes[best_node].name, ii, ii + 1);
                success = false;
                break;
            }
            g->nodes[best_node].budget--;

            int estart = compute_estart(g, best_node, ii);
            int sched_t = -1;

            // Спроба знайти вільний слот у діапазоні [EStart, EStart + II - 1]
            for (int t = estart; t < estart + ii; ++t) {
                if (mrt_can_reserve(&mrt, g, g->nodes[best_node].res, t)) {
                    sched_t = t;
                    break;
                }
            }

            if (sched_t != -1) {
                g->nodes[best_node].sched_time = sched_t;
                mrt_reserve(&mrt, best_node, g->nodes[best_node].res, sched_t);
                unscheduled_count--;
            } else {
                // Відкат (Backtracking): примусово ставимо на EStart, скидаючи конфліктні операції
                sched_t = estart;
                int slot = sched_t % ii;
                ResourceType r = g->nodes[best_node].res;

                int victim = mrt.occupied_by[slot][r][0];
                if (victim != -1 && victim != best_node) {
                    mrt_unreserve(&mrt, victim, r, g->nodes[victim].sched_time);
                    g->nodes[victim].sched_time = -1;
                    unscheduled_count++;
                }

                g->nodes[best_node].sched_time = sched_t;
                mrt_reserve(&mrt, best_node, r, sched_t);
                unscheduled_count--;
            }
        }

        if (success) {
            *final_ii = ii;
            int max_t = 0;
            for (int i = 0; i < g->node_count; ++i) {
                int end_t = g->nodes[i].sched_time + g->nodes[i].latency;
                if (end_t > max_t) max_t = end_t;
            }
            *final_length = max_t;
            return true;
        }

        ii++;
    }

    return false;
}

int main(void) {
    Graph g = {
        .node_count = 4,
        .edge_count = 4,
        .res_units = { [RES_MEM] = 2, [RES_ALU] = 1, [RES_MUL] = 1 },
        .nodes = {
            { .name = "Load_A", .res = RES_MEM, .latency = 2 },
            { .name = "Load_B", .res = RES_MEM, .latency = 2 },
            { .name = "Multiply", .res = RES_MUL, .latency = 2 },
            { .name = "Accumulate", .res = RES_ALU, .latency = 1 }
        },
        .edges = {
            { .src = 0, .dst = 2, .latency = 2, .distance = 0 }, // Load_A -> Mul
            { .src = 1, .dst = 2, .latency = 2, .distance = 0 }, // Load_B -> Mul
            { .src = 2, .dst = 3, .latency = 2, .distance = 0 }, // Mul -> Acc
            { .src = 3, .dst = 3, .latency = 1, .distance = 1 }  // Acc[i] -> Acc[i+1] (рекурентність)
        }
    };

    printf("=== Планувальник Iterative Modulo Scheduling (C) ===\n\n");
    int final_ii = 0;
    int sched_len = 0;

    if (ims_schedule(&g, &final_ii, &sched_len)) {
        int stages = (sched_len + final_ii - 1) / final_ii;
        printf("\nРозклад побудовано успішно!\n");
        printf("Інтервал ініціалізації (II): %d такт(ів)\n", final_ii);
        printf("Загальна довжина розкладу:   %d тактів\n", sched_len);
        printf("Кількість стадій конвеєра:   %d\n\n", stages);

        printf("Таблиця розміщення інструкцій:\n");
        printf("%-12s | %-10s | %-8s | %-12s\n", "Операція", "Ресурс", "Такт t", "Стадія");
        printf("-------------+------------+----------+-------------\n");
        for (int i = 0; i < g.node_count; ++i) {
            const char *res_str = (g.nodes[i].res == RES_MEM) ? "MEM" :
                                  (g.nodes[i].res == RES_ALU) ? "ALU" : "MUL";
            int stage = g.nodes[i].sched_time / final_ii;
            printf("%-12s | %-10s | %-8d | Стадія %d\n",
                   g.nodes[i].name, res_str, g.nodes[i].sched_time, stage);
        }
    } else {
        printf("Не вдалося знайти допустимий розклад у межах MAX_II.\n");
    }

    return 0;
}
