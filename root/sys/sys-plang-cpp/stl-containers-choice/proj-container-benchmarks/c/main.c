/* C11: Дінамичний суцільний масив проти зв'язаного списку вузлів */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>

typedef struct Node {
    int32_t data;
    struct Node* next;
} Node;

typedef struct {
    double duration_ms;
    int64_t total_sum;
} BenchResult;

BenchResult bench_c_array(size_t count) {
    int32_t* arr = (int32_t*)malloc(count * sizeof(int32_t));
    for (size_t i = 0; i < count; ++i) arr[i] = (int32_t)(i + 1);

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);
    
    int64_t sum = 0;
    for (size_t i = 0; i < count; ++i) {
        sum += arr[i];
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    free(arr);

    double ms = (end.tv_sec - start.tv_sec) * 1000.0 + (end.tv_nsec - start.tv_nsec) / 1e6;
    return (BenchResult){ms, sum};
}

BenchResult bench_c_list(size_t count) {
    Node* head = NULL;
    Node* tail = NULL;
    for (size_t i = 0; i < count; ++i) {
        Node* node = (Node*)malloc(sizeof(Node));
        node->data = (int32_t)(i + 1);
        node->next = NULL;
        if (!tail) head = node;
        else tail->next = node;
        tail = node;
    }

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    int64_t sum = 0;
    Node* curr = head;
    while (curr) {
        sum += curr->data;
        curr = curr->next;
    }

    clock_gettime(CLOCK_MONOTONIC, &end);

    /* Звільнення пам'яті */
    curr = head;
    while (curr) {
        Node* tmp = curr;
        curr = curr->next;
        free(tmp);
    }

    double ms = (end.tv_sec - start.tv_sec) * 1000.0 + (end.tv_nsec - start.tv_nsec) / 1e6;
    return (BenchResult){ms, sum};
}

int main(void) {
    const size_t N = 10000000;
    BenchResult res_arr = bench_c_array(N);
    BenchResult res_lst = bench_c_list(N);

    printf("Array sum: %lld in %.2f ms\n", (long long)res_arr.total_sum, res_arr.duration_ms);
    printf("List sum:  %lld in %.2f ms\n", (long long)res_lst.total_sum, res_lst.duration_ms);
    printf("Прискорення Array відносно List: %.2fx\n", res_lst.duration_ms / res_arr.duration_ms);
    return 0;
}
