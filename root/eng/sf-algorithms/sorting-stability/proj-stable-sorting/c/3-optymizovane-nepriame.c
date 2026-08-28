/* C: Непряме сортування масиву індексів з гарантованою стійкістю */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int id;
    int priority;
    char payload[256]; /* Важка структура даних */
} LargeTask;

/* Глобальний контекст для порівняння в qsort_r або через статичний вказівник */
static const LargeTask *g_tasks = NULL;

int compare_indirect(const void *a, const void *b) {
    size_t idx_a = *(const size_t *)a;
    size_t idx_b = *(const size_t *)b;

    if (g_tasks[idx_a].priority != g_tasks[idx_b].priority) {
        return g_tasks[idx_b].priority - g_tasks[idx_a].priority; /* Спадіння */
    }

    /* Рівність пріоритетів: порівнюємо сам індекс для збереження стійкості */
    if (idx_a < idx_b) return -1;
    if (idx_a > idx_b) return 1;
    return 0;
}

void indirect_stable_sort(const LargeTask *tasks, size_t n, size_t *out_indices) {
    for (size_t i = 0; i < n; i++) {
        out_indices[i] = i;
    }
    g_tasks = tasks;
    qsort(out_indices, n, sizeof(size_t), compare_indirect);
    g_tasks = NULL;
}

int main(void) {
    LargeTask tasks[] = {
        {101, 3, "Завдання 1"},
        {102, 5, "Завдання 2 (перше з пріоритетом 5)"},
        {103, 3, "Завдання 3"},
        {104, 5, "Завдання 4 (друге з пріоритетом 5)"}
    };
    size_t n = sizeof(tasks) / sizeof(tasks[0]);
    size_t *indices = (size_t *)malloc(n * sizeof(size_t));

    indirect_stable_sort(tasks, n, indices);

    printf("=== Відсортовані індекси завдань ===\n");
    for (size_t i = 0; i < n; i++) {
        size_t idx = indices[i];
        printf("  Опосередкована позиція [%zu] -> Task ID: %d, Priority: %d (%s)\n",
               i, tasks[idx].id, tasks[idx].priority, tasks[idx].payload);
    }

    free(indices);
    return 0;
}
