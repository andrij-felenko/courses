/* C: Декорувальник ключів для гарантування стійкості будь-якого нестійкого сортувальника */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    int key;
    char payload[64];
} Record;

typedef struct {
    Record data;
    size_t original_index;
} DecoratedRecord;

/* Спеціальний компаратор: якщо ключі однакові, перемагає той, чий початковий індекс менший */
int decorated_comparator(const void *a, const void *b) {
    const DecoratedRecord *da = (const DecoratedRecord *)a;
    const DecoratedRecord *db = (const DecoratedRecord *)b;

    if (da->data.key != db->data.key) {
        return da->data.key - db->data.key; /* Основне сортування за зростанням ключів */
    }

    /* Рівність ключів: суворе порівняння за початковим індексом для стійкості */
    if (da->original_index < db->original_index) return -1;
    if (da->original_index > db->original_index) return 1;
    return 0;
}

void stable_qsort_wrapper(Record *arr, size_t n) {
    DecoratedRecord *decorated = (DecoratedRecord *)malloc(n * sizeof(DecoratedRecord));
    if (!decorated) return;

    /* Крок 1: Декорування (збереження початкового індексу) */
    for (size_t i = 0; i < n; i++) {
        decorated[i].data = arr[i];
        decorated[i].original_index = i;
    }

    /* Крок 2: Виклик НЕСТІЙКОГО qsort з розширеним компаратором */
    qsort(decorated, n, sizeof(DecoratedRecord), decorated_comparator);

    /* Крок 3: Розпакування (Un-decorate) */
    for (size_t i = 0; i < n; i++) {
        arr[i] = decorated[i].data;
    }

    free(decorated);
}

int main(void) {
    Record items[] = {
        {10, "Запис A"},
        {5,  "Запис B (перший з 5)"},
        {20, "Запис C"},
        {5,  "Запис D (другий з 5)"},
        {5,  "Запис E (третій з 5)"}
    };
    size_t n = sizeof(items) / sizeof(items[0]);

    printf("=== До сортування ===\n");
    for (size_t i = 0; i < n; i++) {
        printf("  [%zu] Key: %d, Payload: %s\n", i, items[i].key, items[i].payload);
    }

    stable_qsort_wrapper(items, n);

    printf("\n=== Після декорованого нестійкого qsort ===\n");
    for (size_t i = 0; i < n; i++) {
        printf("  [%zu] Key: %d, Payload: %s\n", i, items[i].key, items[i].payload);
    }

    return 0;
}
