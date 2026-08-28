#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define INF_DIST  (1LL << 60)
#define NEG_INF   (-INF_DIST)
#define NO_NEXT   (-1)

typedef struct {
    int n;
    int64_t *dist;   // лінійний масив розміру n * n
    int *next;       // матриця наступних переходів n * n
} FloydWarshallResult;

static inline int idx(int n, int i, int j) {
    return i * n + j;
}

FloydWarshallResult* fw_create(int n) {
    FloydWarshallResult *fw = (FloydWarshallResult*)malloc(sizeof(FloydWarshallResult));
    if (!fw) return NULL;
    
    fw->n = n;
    fw->dist = (int64_t*)malloc((size_t)n * n * sizeof(int64_t));
    fw->next = (int*)malloc((size_t)n * n * sizeof(int));
    
    if (!fw->dist || !fw->next) {
        free(fw->dist);
        free(fw->next);
        free(fw);
        return NULL;
    }
    
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            int p = idx(n, i, j);
            if (i == j) {
                fw->dist[p] = 0;
                fw->next[p] = j;
            } else {
                fw->dist[p] = INF_DIST;
                fw->next[p] = NO_NEXT;
            }
        }
    }
    return fw;
}

void fw_add_edge(FloydWarshallResult *fw, int u, int v, int64_t weight) {
    if (u < 0 || u >= fw->n || v < 0 || v >= fw->n) return;
    int p = idx(fw->n, u, v);
    if (weight < fw->dist[p]) {
        fw->dist[p] = weight;
        fw->next[p] = v;
    }
}

void fw_compute(FloydWarshallResult *fw) {
    int n = fw->n;
    int64_t *d = fw->dist;
    int *nxt = fw->next;
    
    // Фаза 1: Класичний динамічний перебір проміжних вершин k
    for (int k = 0; k < n; ++k) {
        for (int i = 0; i < n; ++i) {
            int64_t dik = d[idx(n, i, k)];
            if (dik >= INF_DIST) continue;
            
            for (int j = 0; j < n; ++j) {
                int64_t dkj = d[idx(n, k, j)];
                if (dkj >= INF_DIST) continue;
                
                int64_t new_dist = dik + dkj;
                int pij = idx(n, i, j);
                if (new_dist < d[pij]) {
                    d[pij] = new_dist;
                    nxt[pij] = nxt[idx(n, i, k)];
                }
            }
        }
    }
    
    // Фаза 2: Поширення впливу від'ємних циклів (-INF)
    for (int k = 0; k < n; ++k) {
        if (d[idx(n, k, k)] < 0) {
            for (int i = 0; i < n; ++i) {
                for (int j = 0; j < n; ++j) {
                    if (d[idx(n, i, k)] < INF_DIST && d[idx(n, k, j)] < INF_DIST) {
                        d[idx(n, i, j)] = NEG_INF;
                        nxt[idx(n, i, j)] = NO_NEXT;
                    }
                }
            }
        }
    }
}

int fw_reconstruct_path(const FloydWarshallResult *fw, int u, int v, int *out_path, int max_len) {
    if (u < 0 || u >= fw->n || v < 0 || v >= fw->n) return 0;
    int p = idx(fw->n, u, v);
    if (fw->dist[p] == INF_DIST || fw->dist[p] == NEG_INF) return 0;
    if (fw->next[p] == NO_NEXT) return 0;
    
    int count = 0;
    int cur = u;
    if (count < max_len) out_path[count++] = cur;
    
    // Захист від зациклення: шлях у простому графі не може перевищувати n вершин
    int step_limit = 0;
    while (cur != v && step_limit < fw->n) {
        cur = fw->next[idx(fw->n, cur, v)];
        if (cur == NO_NEXT || count >= max_len) return 0;
        out_path[count++] = cur;
        step_limit++;
    }
    
    if (cur != v) return 0; // виявлено зациклення або пошкоджений шлях
    return count;
}

void fw_destroy(FloydWarshallResult *fw) {
    if (!fw) return;
    free(fw->dist);
    free(fw->next);
    free(fw);
}
