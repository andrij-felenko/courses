#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <assert.h>

/* Наївна еталонна функція O(N) */
int32_t naive_rmq(const int32_t *arr, size_t l, size_t r) {
    int32_t min_val = arr[l];
    for (size_t i = l + 1; i <= r; ++i) {
        if (arr[i] < min_val) min_val = arr[i];
    }
    return min_val;
}

/* Фазинг-тест для перевірки коректності */
void run_fuzz_test(size_t n, size_t num_queries) {
    int32_t *arr = (int32_t *)malloc(n * sizeof(int32_t));
    for (size_t i = 0; i < n; ++i) {
        arr[i] = (rand() % 2000000) - 1000000;
    }

    sparse_table_t *st = st_create(arr, n);
    assert(st != NULL);

    for (size_t q = 0; q < num_queries; ++q) {
        size_t l = rand() % n;
        size_t r = rand() % n;
        if (l > r) { size_t tmp = l; l = r; r = tmp; }

        int32_t st_res;
        bool ok = st_query_min(st, l, r, &st_res);
        assert(ok);

        int32_t expected = naive_rmq(arr, l, r);
        assert(st_res == expected);
    }

    st_destroy(st);
    free(arr);
    printf("Фазинг-тест успішно пройдено (%zu запитів на N=%zu).\n", num_queries, n);
}
