#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define INF (1LL << 60)
#define NIL (-1)

void reconstruct_path(int u, int v, int n, int *next_matrix, int64_t *dist_matrix) {
    if (dist_matrix[u * n + v] >= INF || next_matrix[u * n + v] == NIL) {
        printf("Шлях між %d та %d не існує\n", u, v);
        return;
    }
    
    printf("Маршрут: %d", u);
    int cur = u;
    int steps = 0;
    while (cur != v && steps < n) {
        cur = next_matrix[cur * n + v];
        if (cur == NIL) {
            printf(" -> [Помилка розриву]");
            break;
        }
        printf(" -> %d", cur);
        steps++;
    }
    printf("\n");
}
