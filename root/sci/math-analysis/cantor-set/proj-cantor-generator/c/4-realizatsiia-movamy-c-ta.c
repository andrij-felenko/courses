#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <math.h>

typedef struct {
    double start;
    double end;
} cantor_interval_t;

typedef struct {
    cantor_interval_t* data;
    size_t count;
    size_t capacity;
} cantor_set_t;

cantor_set_t* cantor_set_create(size_t initial_capacity) {
    cantor_set_t* set = (cantor_set_t*)malloc(sizeof(cantor_set_t));
    if (!set) return NULL;
    set->data = (cantor_interval_t*)malloc(initial_capacity * sizeof(cantor_interval_t));
    if (!set->data) {
        free(set);
        return NULL;
    }
    set->count = 0;
    set->capacity = initial_capacity;
    return set;
}

void cantor_set_free(cantor_set_t* set) {
    if (set) {
        free(set->data);
        free(set);
    }
}

bool cantor_set_append(cantor_set_t* set, double start, double end) {
    if (set->count >= set->capacity) {
        size_t new_cap = set->capacity * 2;
        cantor_interval_t* new_data = (cantor_interval_t*)realloc(set->data, new_cap * sizeof(cantor_interval_t));
        if (!new_data) return false;
        set->data = new_data;
        set->capacity = new_cap;
    }
    set->data[set->count].start = start;
    set->data[set->count].end = end;
    set->count++;
    return true;
}

cantor_set_t* cantor_generate_level(int level) {
    size_t expected_count = (size_t)1 << level;
    cantor_set_t* current = cantor_set_create(expected_count);
    if (!current) return NULL;

    cantor_set_append(current, 0.0, 1.0);

    for (int lvl = 0; lvl < level; lvl++) {
        cantor_set_t* next = cantor_set_create(current->count * 2);
        if (!next) {
            cantor_set_free(current);
            return NULL;
        }

        for (size_t i = 0; i < current->count; i++) {
            double a = current->data[i].start;
            double b = current->data[i].end;
            double third = (b - a) / 3.0;

            cantor_set_append(next, a, a + third);
            cantor_set_append(next, b - third, b);
        }

        cantor_set_free(current);
        current = next;
    }

    return current;
}

bool cantor_contains_point(double x, int max_depth) {
    if (x < 0.0 || x > 1.0) return false;

    double curr = x;
    for (int i = 0; i < max_depth; i++) {
        curr *= 3.0;
        int digit = (int)floor(curr);
        if (digit == 1) {
            return false;
        }
        if (digit == 2) {
            curr -= 2.0;
        }
    }
    return true;
}

double cantor_estimate_box_counting_dim(int level) {
    cantor_set_t* set = cantor_generate_level(level);
    if (!set) return -1.0;

    double epsilon = pow(3.0, -level);
    double num_boxes = (double)set->count;

    double dimension = log(num_boxes) / log(1.0 / epsilon);

    cantor_set_free(set);
    return dimension;
}

int main(void) {
    int depth = 5;
    printf("=== Обчислення триадної множини Кантора (Рівень %d) ===\n", depth);

    cantor_set_t* cantor = cantor_generate_level(depth);
    if (cantor) {
        printf("Кількість інтервалів на рівні %d: %zu\n", depth, cantor->count);
        printf("Перші 4 інтервали:\n");
        for (size_t i = 0; i < 4 && i < cantor->count; i++) {
            printf("  [%f, %f]\n", cantor->data[i].start, cantor->data[i].end);
        }
        cantor_set_free(cantor);
    }

    double test_points[] = {0.0, 0.25, 0.3333333333333333, 0.5, 0.75, 1.0};
    size_t num_tests = sizeof(test_points) / sizeof(test_points[0]);

    printf("\nПеревірка належності точок (глибина 20):\n");
    for (size_t i = 0; i < num_tests; i++) {
        bool in_cantor = cantor_contains_point(test_points[i], 20);
        printf("  x = %.4f -> %s\n", test_points[i], in_cantor ? "Належить (C)" : "Вилучено (U)");
    }

    printf("\nЧисельна оцінка фрактальної вимірності:\n");
    for (int k = 1; k <= 8; k++) {
        double dim = cantor_estimate_box_counting_dim(k);
        printf("  Рівень k = %d: N = %d, dim = %.6f\n", k, 1 << k, dim);
    }

    return 0;
}
