#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_NODES 10
#define INF 9999

typedef struct {
    int cost;
    int next_hop;
} RouteEntry;

typedef struct {
    int id;
    int num_neighbors;
    int neighbors[MAX_NODES];
    int link_costs[MAX_NODES];
    RouteEntry table[MAX_NODES];
} Router;

void router_init(Router *r, int id, int total_nodes) {
    r->id = id;
    r->num_neighbors = 0;
    for (int i = 0; i < total_nodes; i++) {
        if (i == id) {
            r->table[i].cost = 0;
            r->table[i].next_hop = id;
        } else {
            r->table[i].cost = INF;
            r->table[i].next_hop = -1;
        }
        r->link_costs[i] = INF;
    }
}

void router_add_neighbor(Router *r, int neighbor_id, int cost) {
    r->neighbors[r->num_neighbors++] = neighbor_id;
    r->link_costs[neighbor_id] = cost;
    r->table[neighbor_id].cost = cost;
    r->table[neighbor_id].next_hop = neighbor_id;
}

// Підготовка вектора з урахуванням Poison Reverse для конкретного сусіда
void prepare_vector(const Router *r, int target_neighbor, int *out_vector, int total_nodes) {
    for (int d = 0; d < total_nodes; d++) {
        // Якщо наш шлях до d іде через target_neighbor, отруюємо маршрут
        if (d != r->id && r->table[d].next_hop == target_neighbor) {
            out_vector[d] = INF;
        } else {
            out_vector[d] = r->table[d].cost;
        }
    }
}

// Оновлення таблиці при отриманні вектора від сусіда neighbor_id
bool update_from_neighbor(Router *r, int neighbor_id, const int *received_vector, int total_nodes) {
    bool changed = false;
    int cost_to_neighbor = r->link_costs[neighbor_id];

    if (cost_to_neighbor >= INF) return false;

    for (int d = 0; d < total_nodes; d++) {
        if (d == r->id) continue;

        int dist_via_neighbor = received_vector[d];
        int new_cost = (dist_via_neighbor >= INF) ? INF : (cost_to_neighbor + dist_via_neighbor);

        if (new_cost < r->table[d].cost) {
            r->table[d].cost = new_cost;
            r->table[d].next_hop = neighbor_id;
            changed = true;
        }
    }
    return changed;
}

void print_table(const Router *r, int total_nodes) {
    printf("--- Таблиця маршрутизації вузла %d ---\n", r->id);
    printf("Ціль\tДистанція\tНаступний хоп\n");
    for (int i = 0; i < total_nodes; i++) {
        if (r->table[i].cost >= INF) {
            printf("%d\tINF\t\t-\n", i);
        } else {
            printf("%d\t%d\t\t%d\n", i, r->table[i].cost, r->table[i].next_hop);
        }
    }
    printf("\n");
}

int main(void) {
    const int total_nodes = 4;
    Router routers[4];

    for (int i = 0; i < total_nodes; i++) {
        router_init(&routers[i], i, total_nodes);
    }

    // Мережеві зв'язки: 0-1 (вага 1), 1-2 (вага 3), 0-2 (вага 7), 2-3 (вага 2)
    router_add_neighbor(&routers[0], 1, 1);
    router_add_neighbor(&routers[0], 2, 7);

    router_add_neighbor(&routers[1], 0, 1);
    router_add_neighbor(&routers[1], 2, 3);

    router_add_neighbor(&routers[2], 0, 7);
    router_add_neighbor(&routers[2], 1, 3);
    router_add_neighbor(&routers[2], 3, 2);

    router_add_neighbor(&routers[3], 2, 2);

    int iteration = 0;
    bool any_changed = true;
    int temp_vector[MAX_NODES];

    printf("=== Старт дистанційно-векторного алгоритму ===\n\n");

    while (any_changed && iteration < 10) {
        any_changed = false;
        iteration++;
        printf(">>> Ітерація %d <<<\n", iteration);

        for (int u = 0; u < total_nodes; u++) {
            for (int k = 0; k < routers[u].num_neighbors; k++) {
                int v = routers[u].neighbors[k];
                prepare_vector(&routers[u], v, temp_vector, total_nodes);
                if (update_from_neighbor(&routers[v], u, temp_vector, total_nodes)) {
                    any_changed = true;
                }
            }
        }
    }

    printf("Збіжність досягнута за %d ітерацій.\n\n", iteration);
    for (int i = 0; i < total_nodes; i++) {
        print_table(&routers[i], total_nodes);
    }

    return 0;
}
