#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_NODES 10
#define MAX_COMMODITIES 5

typedef struct {
    int u;
    int v;
    int capacity;
} Edge;

typedef struct {
    int num_nodes;
    int num_edges;
    int num_commodities;
    Edge edges[20];
    int queue[MAX_NODES][MAX_COMMODITIES];
} Network;

void network_init(Network *net, int n, int num_comm) {
    net->num_nodes = n;
    net->num_edges = 0;
    net->num_commodities = num_comm;
    for (int i = 0; i < n; i++) {
        for (int c = 0; c < num_comm; c++) {
            net->queue[i][c] = 0;
        }
    }
}

void network_add_edge(Network *net, int u, int v, int cap) {
    net->edges[net->num_edges].u = u;
    net->edges[net->num_edges].v = v;
    net->edges[net->num_edges].capacity = cap;
    net->num_edges++;
}

void backpressure_step(Network *net) {
    // Тимчасовий масив для накопичення змін черг за один крок
    int delta[MAX_NODES][MAX_COMMODITIES] = {0};

    for (int e = 0; e < net->num_edges; e++) {
        int u = net->edges[e].u;
        int v = net->edges[e].v;
        int cap = net->edges[e].capacity;

        int max_weight = 0;
        int best_commodity = -1;

        // Пошук товару з максимальним різницевим тиском
        for (int c = 0; c < net->num_commodities; c++) {
            int weight = net->queue[u][c] - net->queue[v][c];
            if (weight > max_weight) {
                max_weight = weight;
                best_commodity = c;
            }
        }

        // Якщо є позитивний тиск, виконуємо передачу
        if (best_commodity != -1 && max_weight > 0) {
            int packets_to_send = net->queue[u][best_commodity];
            if (packets_to_send > cap) {
                packets_to_send = cap;
            }

            delta[u][best_commodity] -= packets_to_send;
            delta[v][best_commodity] += packets_to_send;

            printf("  Ребро (%d->%d): переслано %d пакетів товару %d (тиск = %d)\n",
                   u, v, packets_to_send, best_commodity, max_weight);
        }
    }

    // Оновлюємо стан черг
    for (int i = 0; i < net->num_nodes; i++) {
        for (int c = 0; c < net->num_commodities; c++) {
            net->queue[i][c] += delta[i][c];
            // Списання пакетів при досягненні вузла-призначення
            if (i == c) {
                net->queue[i][c] = 0;
            }
        }
    }
}

int main(void) {
    Network net;
    network_init(&net, 4, 2);

    // Додаємо орієнтовані ребра з ємностями
    network_add_edge(&net, 0, 1, 5);
    network_add_edge(&net, 0, 2, 5);
    network_add_edge(&net, 1, 3, 4);
    network_add_edge(&net, 2, 3, 4);

    // Початкове заповнення черг трафіком
    net.queue[0][3] = 20; // 20 пакетів у вузлі 0 із призначенням у вузол 3

    printf("=== Початковий стан черги у вузлі 0: %d ===\n", net.queue[0][3]);

    for (int t = 1; t <= 4; t++) {
        printf("\nТакт %d:\n", t);
        backpressure_step(&net);
        printf("Стан черг: Node 0=%d, Node 1=%d, Node 2=%d, Node 3=%d\n",
               net.queue[0][3], net.queue[1][3], net.queue[2][3], net.queue[3][3]);
    }

    return 0;
}
