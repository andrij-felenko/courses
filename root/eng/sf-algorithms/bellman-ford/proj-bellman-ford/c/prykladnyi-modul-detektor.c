#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>
#include <string.h>

#define EPSILON 1e-9

typedef struct {
    char from[8];
    char to[8];
    double rate;
} CurrencyRate;

typedef struct {
    int src;
    int dest;
    double weight;
} ArbitrageEdge;

void detect_currency_arbitrage(int num_currencies, int num_rates, const CurrencyRate* rates) {
    ArbitrageEdge* edges = (ArbitrageEdge*)malloc(num_rates * sizeof(ArbitrageEdge));
    
    for (int i = 0; i < num_rates; ++i) {
        // Конвертація курсу у від'ємний логарифм
        edges[i].src = rates[i].from[0] - 'A';
        edges[i].dest = rates[i].to[0] - 'A';
        edges[i].weight = -log(rates[i].rate);
    }

    double* dist = (double*)malloc(num_currencies * sizeof(double));
    int* parent = (int*)malloc(num_currencies * sizeof(int));
    for (int i = 0; i < num_currencies; ++i) {
        dist[i] = 0.0; // Стартуємо з супер-джерела 0 від усіх
        parent[i] = -1;
    }

    // Раунди послаблень з порогом EPSILON
    for (int iter = 0; iter < num_currencies - 1; ++iter) {
        for (int i = 0; i < num_rates; ++i) {
            int u = edges[i].src;
            int v = edges[i].dest;
            double w = edges[i].weight;
            if (dist[u] + w < dist[v] - EPSILON) {
                dist[v] = dist[u] + w;
                parent[v] = u;
            }
        }
    }

    // Детекція від'ємного циклу
    int cycle_node = -1;
    for (int i = 0; i < num_rates; ++i) {
        int u = edges[i].src;
        int v = edges[i].dest;
        double w = edges[i].weight;
        if (dist[u] + w < dist[v] - EPSILON) {
            cycle_node = v;
            parent[v] = u;
            break;
        }
    }

    if (cycle_node != -1) {
        for (int i = 0; i < num_currencies; ++i) {
            cycle_node = parent[cycle_node];
        }
        printf("Знайдено прибутковий арбітражний цикл!\n");
    } else {
        printf("Арбітражних можливостей не виявлено.\n");
    }

    free(edges);
    free(dist);
    free(parent);
}

int main(void) {
    CurrencyRate rates[] = {
        {"USD", "EUR", 0.92},
        {"EUR", "GBP", 0.86},
        {"GBP", "USD", 1.28}
    };
    detect_currency_arbitrage(3, 3, rates);
    return 0;
}
