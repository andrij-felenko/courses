/* C11: Повний бенчмарк сортування з ініціалізацією та вимірюванням часу */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <locale.h>
#include <time.h>

static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

// Функція генерації тестового набору даних
static char **generate_test_data(size_t count) {
    static const char *words[] = {
        "апельсин", "Apple", "банан", "Бджола", "вишня", "Арбуз", 
        "гараж", "Ґрунт", "100", "20", "Zebra", "яблуко", "єнот", "Їжак"
    };
    size_t num_words = sizeof(words) / sizeof(words[0]);

    char **array = malloc(count * sizeof(char *));
    if (!array) return NULL;

    for (size_t i = 0; i < count; ++i) {
        char buf[256];
        snprintf(buf, sizeof(buf), "%s_%s_%zu", 
                 words[i % num_words], words[(i * 3) % num_words], i);
        array[i] = strdup(buf);
    }
    return array;
}

static void free_test_data(char **array, size_t count) {
    for (size_t i = 0; i < count; ++i) free(array[i]);
    free(array);
}

int cmp_strcmp(const void *a, const void *b) {
    return strcmp(*(const char **)a, *(const char **)b);
}

int cmp_strcoll(const void *a, const void *b) {
    return strcoll(*(const char **)a, *(const char **)b);
}

typedef struct {
    char *orig;
    char *key;
} KeyEntry;

int cmp_key_entry(const void *a, const void *b) {
    return strcmp(((const KeyEntry *)a)->key, ((const KeyEntry *)b)->key);
}

void run_benchmark_c(size_t count) {
    printf("--- Генерація %zu тестових рядків ---\n", count);
    char **input_data = generate_test_data(count);
    if (!input_data) return;

    char **work_array = malloc(count * sizeof(char *));

    // 1. Бенчмарк strcmp (LC_ALL=C)
    setlocale(LC_ALL, "C");
    memcpy(work_array, input_data, count * sizeof(char *));
    double t0 = get_time_sec();
    qsort(work_array, count, sizeof(char *), cmp_strcmp);
    double t1 = get_time_sec();
    printf("[C] strcmp (двійковий режим C): %.4f сек\n", t1 - t0);

    // 2. Бенчмарк strcoll (мовна локаль uk_UA.UTF-8)
    if (setlocale(LC_ALL, "uk_UA.UTF-8") == NULL) {
        setlocale(LC_ALL, "en_US.UTF-8");
    }
    memcpy(work_array, input_data, count * sizeof(char *));
    t0 = get_time_sec();
    qsort(work_array, count, sizeof(char *), cmp_strcoll);
    t1 = get_time_sec();
    printf("[C] strcoll (мовний режим UTF-8): %.4f сек\n", t1 - t0);

    // 3. Оптимізований варіант з кшуванням strxfrm
    t0 = get_time_sec();
    KeyEntry *entries = malloc(count * sizeof(KeyEntry));
    for (size_t i = 0; i < count; ++i) {
        entries[i].orig = input_data[i];
        size_t len = strxfrm(NULL, input_data[i], 0) + 1;
        entries[i].key = malloc(len);
        if (entries[i].key) {
            strxfrm(entries[i].key, input_data[i], len);
        }
    }

    qsort(entries, count, sizeof(KeyEntry), cmp_key_entry);
    t1 = get_time_sec();

    printf("[C] strxfrm + strcmp (трансформовані ключі): %.4f сек\n", t1 - t0);

    for (size_t i = 0; i < count; ++i) free(entries[i].key);
    free(entries);
    free(work_array);
    free_test_data(input_data, count);
}

int main(void) {
    run_benchmark_c(300000);
    return 0;
}
