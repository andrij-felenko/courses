#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

/* Структура для збереження результатів маркування */
typedef struct {
    int* output_grid;          /* Результуюча ґратка розміром L x L з канонічними мітками */
    int* cluster_sizes;        /* Масив розмірів кластерів, індексація 1..num_clusters */
    int num_clusters;          /* Загальна кількість знайдених зв'язаних кластерів */
    int max_cluster_size;      /* Розмір найбільшого кластера */
    bool has_spanning_cluster; /* Чи існує протікаючий кластер (від top до bottom) */
} HKResult2D;

/* Внутрішній контекст системи неперетинних множин */
typedef struct {
    int* labels;               /* Масив еквівалентностей та розмірів */
    int capacity;              /* Поточна місткість масиву */
    int max_label;             /* Найбільша видана тимчасова мітка */
} HKDisjointSet;

/* Ініціалізація структури DSU */
static bool dsu_init(HKDisjointSet* dsu, int initial_capacity) {
    dsu->capacity = initial_capacity > 1024 ? initial_capacity : 1024;
    dsu->labels = (int*)malloc((size_t)dsu->capacity * sizeof(int));
    if (!dsu->labels) return false;
    memset(dsu->labels, 0, (size_t)dsu->capacity * sizeof(int));
    dsu->max_label = 0;
    return true;
}

/* Звільнення пам'яті DSU */
static void dsu_free(HKDisjointSet* dsu) {
    if (dsu->labels) {
        free(dsu->labels);
        dsu->labels = NULL;
    }
    dsu->capacity = 0;
    dsu->max_label = 0;
}

/* Динамічне розширення масиву міток */
static bool dsu_grow(HKDisjointSet* dsu) {
    int new_capacity = dsu->capacity * 2;
    int* new_labels = (int*)realloc(dsu->labels, (size_t)new_capacity * sizeof(int));
    if (!new_labels) return false;
    memset(new_labels + dsu->capacity, 0, (size_t)dsu->capacity * sizeof(int));
    dsu->labels = new_labels;
    dsu->capacity = new_capacity;
    return true;
}

/* Створення нової мітки для нового кластера розміру 1 */
static int dsu_make_cluster(HKDisjointSet* dsu) {
    dsu->max_label++;
    if (dsu->max_label >= dsu->capacity) {
        if (!dsu_grow(dsu)) return -1;
    }
    dsu->labels[dsu->max_label] = -1; /* Від'ємне значення: розмір 1 */
    return dsu->max_label;
}

/* Пошук канонічного кореня з повним стисненням шляхів */
static int dsu_find(HKDisjointSet* dsu, int x) {
    int root = x;
    while (dsu->labels[root] > 0) {
        root = dsu->labels[root];
    }
    /* Стиснення шляхів: усі проміжні вузли перенаправляються прямо на root */
    int curr = x;
    while (curr != root) {
        int next = dsu->labels[curr];
        dsu->labels[curr] = root;
        curr = next;
    }
    return root;
}

/* Злиття двох кластерів при колізії міток */
static int dsu_union(HKDisjointSet* dsu, int root1, int root2) {
    if (root1 == root2) return root1;

    /* Об'єднуємо: менший номер стає коренем */
    if (root1 > root2) {
        int temp = root1;
        root1 = root2;
        root2 = temp;
    }

    /* Підсумовуємо розміри кластерів (обидва значення від'ємні) */
    dsu->labels[root1] += dsu->labels[root2];
    /* Робимо root2 дочірнім для root1 */
    dsu->labels[root2] = root1;

    return root1;
}

/* Головна функція алгоритму Гошена-Копельмана для 2D ґратки */
HKResult2D hoshen_kopelman_2d(const uint8_t* binary_input, int width, int height) {
    HKResult2D result;
    memset(&result, 0, sizeof(HKResult2D));

    if (!binary_input || width <= 0 || height <= 0) return result;

    size_t total_sites = (size_t)width * (size_t)height;
    result.output_grid = (int*)malloc(total_sites * sizeof(int));
    if (!result.output_grid) return result;

    HKDisjointSet dsu;
    if (!dsu_init(&dsu, (width * height) / 4 + 16)) {
        free(result.output_grid);
        result.output_grid = NULL;
        return result;
    }

    /* Буфер попереднього рядка: O(width) */
    int* prev_row = (int*)calloc((size_t)width, sizeof(int));
    int* curr_row = (int*)calloc((size_t)width, sizeof(int));
    if (!prev_row || !curr_row) {
        free(prev_row);
        free(curr_row);
        free(result.output_grid);
        dsu_free(&dsu);
        return result;
    }

    /* ПРОХІД 1: Растрове сканування рядків */
    for (int r = 0; r < height; ++r) {
        for (int c = 0; c < width; ++c) {
            uint8_t occupied = binary_input[r * width + c];
            if (!occupied) {
                curr_row[c] = 0;
                result.output_grid[r * width + c] = 0;
                continue;
            }

            int top_label = (r > 0) ? prev_row[c] : 0;
            int left_label = (c > 0) ? curr_row[c - 1] : 0;

            if (top_label == 0 && left_label == 0) {
                /* Випадок 1: Новий ізольований кластер */
                int new_lbl = dsu_make_cluster(&dsu);
                curr_row[c] = new_lbl;
                result.output_grid[r * width + c] = new_lbl;
            } else if (top_label > 0 && left_label == 0) {
                /* Випадок 2: Успадкування мітки зверху */
                int root = dsu_find(&dsu, top_label);
                dsu.labels[root]--; /* Збільшуємо розмір кластера на 1 */
                curr_row[c] = root;
                result.output_grid[r * width + c] = root;
            } else if (top_label == 0 && left_label > 0) {
                /* Випадок 3: Успадкування мітки зліва */
                int root = dsu_find(&dsu, left_label);
                dsu.labels[root]--; /* Збільшуємо розмір кластера на 1 */
                curr_row[c] = root;
                result.output_grid[r * width + c] = root;
            } else {
                /* Випадок 4: Колізія міток (Top > 0 та Left > 0) */
                int root_top = dsu_find(&dsu, top_label);
                int root_left = dsu_find(&dsu, left_label);

                if (root_top == root_left) {
                    dsu.labels[root_top]--; /* Вже той самий кластер */
                    curr_row[c] = root_top;
                    result.output_grid[r * width + c] = root_top;
                } else {
                    int merged_root = dsu_union(&dsu, root_top, root_left);
                    dsu.labels[merged_root]--; /* Додаємо поточний вузол */
                    curr_row[c] = merged_root;
                    result.output_grid[r * width + c] = merged_root;
                }
            }
        }
        /* Переносимо поточний рядок у попередній */
        memcpy(prev_row, curr_row, (size_t)width * sizeof(int));
    }

    free(prev_row);
    free(curr_row);

    /* ПРОХІД 2: Канонічна перенумерація та збір статистики */
    int* canonical_map = (int*)calloc((size_t)(dsu.max_label + 1), sizeof(int));
    if (!canonical_map) {
        free(result.output_grid);
        dsu_free(&dsu);
        return result;
    }

    int canonical_counter = 0;
    for (int k = 1; k <= dsu.max_label; ++k) {
        if (dsu.labels[k] < 0) {
            /* Це канонічний корінь */
            canonical_counter++;
            canonical_map[k] = canonical_counter;
        }
    }

    result.num_clusters = canonical_counter;
    result.cluster_sizes = (int*)calloc((size_t)(canonical_counter + 1), sizeof(int));

    /* Заповнюємо масив розмірів за канонічними індексами */
    for (int k = 1; k <= dsu.max_label; ++k) {
        if (dsu.labels[k] < 0) {
            int c_id = canonical_map[k];
            int size = -dsu.labels[k];
            result.cluster_sizes[c_id] = size;
            if (size > result.max_cluster_size) {
                result.max_cluster_size = size;
            }
        }
    }

    /* Замінюємо тимчасові мітки в результуючій ґратці на канонічні 1..K */
    bool* top_touched = (bool*)calloc((size_t)(canonical_counter + 1), sizeof(bool));
    bool* bottom_touched = (bool*)calloc((size_t)(canonical_counter + 1), sizeof(bool));

    for (int r = 0; r < height; ++r) {
        for (int c = 0; c < width; ++c) {
            int raw_lbl = result.output_grid[r * width + c];
            if (raw_lbl > 0) {
                int root = dsu_find(&dsu, raw_lbl);
                int canon = canonical_map[root];
                result.output_grid[r * width + c] = canon;

                if (r == 0) top_touched[canon] = true;
                if (r == height - 1) bottom_touched[canon] = true;
            }
        }
    }

    /* Перевіряємо наявність протікаючого кластера (Top-to-Bottom) */
    result.has_spanning_cluster = false;
    for (int i = 1; i <= canonical_counter; ++i) {
        if (top_touched[i] && bottom_touched[i]) {
            result.has_spanning_cluster = true;
            break;
        }
    }

    free(canonical_map);
    free(top_touched);
    free(bottom_touched);
    dsu_free(&dsu);

    return result;
}

/* Звільнення результату */
void free_hk_result_2d(HKResult2D* res) {
    if (res->output_grid) free(res->output_grid);
    if (res->cluster_sizes) free(res->cluster_sizes);
    memset(res, 0, sizeof(HKResult2D));
}
