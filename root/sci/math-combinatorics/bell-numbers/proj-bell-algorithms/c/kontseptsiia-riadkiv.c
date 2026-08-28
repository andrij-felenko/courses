#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef void (*partition_callback)(const int *a, size_t n, void *user_data);

/* Генерація всіх розбиттів n-множини у форматі RGS (Алгоритм H Дональда Кнута) */
static void generate_rgs_rec(size_t idx, size_t n, int *a, int *m,
                             partition_callback cb, void *user_data) {
    if (idx == n) {
        cb(a, n, user_data);
        return;
    }

    int max_prev = m[idx - 1];
    for (int v = 0; v <= max_prev + 1; ++v) {
        a[idx] = v;
        m[idx] = (v > max_prev) ? v : max_prev;
        generate_rgs_rec(idx + 1, n, a, m, cb, user_data);
    }
}

void generate_all_partitions(size_t n, partition_callback cb, void *user_data) {
    if (n == 0 || !cb) return;

    int *a = (int *)malloc(n * sizeof(int));
    int *m = (int *)malloc(n * sizeof(int));
    if (!a || !m) { free(a); free(m); return; }

    a[0] = 0;
    m[0] = 0;

    generate_rgs_rec(1, n, a, m, cb, user_data);

    free(a);
    free(m);
}

static void print_partition(const int *a, size_t n, void *user_data) {
    size_t *count = (size_t *)user_data;
    (*count)++;

    printf("[%2zu] RGS: (", *count);
    for (size_t i = 0; i < n; ++i) {
        printf("%d%s", a[i], (i + 1 < n) ? ", " : "");
    }
    printf(")\n");
}

int main(void) {
    size_t count = 0;
    const size_t N = 4;
    printf("Усі розбиття для n = 4 (усього B_4 = 15):\n");
    generate_all_partitions(N, print_partition, &count);
    return 0;
}
