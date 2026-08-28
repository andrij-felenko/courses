#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>

#define MAX_ATTRS 8
#define MAX_VAL_LEN 64
#define MAX_TUPLES 256

typedef struct {
    char values[MAX_ATTRS][MAX_VAL_LEN];
    int count;
} Tuple;

typedef struct {
    char name[64];
    char schema[MAX_ATTRS][64];
    int num_attrs;
    Tuple tuples[MAX_TUPLES];
    int num_tuples;
} Relation;

// Перевірка рівності двох кортежів
bool tuple_equals(const Tuple *t1, const Tuple *t2) {
    if (t1->count != t2->count) return false;
    for (int i = 0; i < t1->count; i++) {
        if (strcmp(t1->values[i], t2->values[i]) != 0) return false;
    }
    return true;
}

// Додавання кортежу до відношення з вилученням дублікатів (забезпечення властивостей множини)
bool relation_add_tuple(Relation *rel, const Tuple *t) {
    if (rel->num_tuples >= MAX_TUPLES) return false;
    for (int i = 0; i < rel->num_tuples; i++) {
        if (tuple_equals(&rel->tuples[i], t)) return true; // Вже існує
    }
    rel->tuples[rel->num_tuples++] = *t;
    return true;
}

// Пошук індексу атрибута у схемі
int relation_find_attr(const Relation *rel, const char *attr_name) {
    for (int i = 0; i < rel->num_attrs; i++) {
        if (strcmp(rel->schema[i], attr_name) == 0) return i;
    }
    return -1;
}

// Оператор Селекції: sigma_{attr = val}(R)
Relation relation_select(const Relation *src, const char *attr_name, const char *target_val) {
    Relation res;
    snprintf(res.name, sizeof(res.name), "sigma_%s=%s(%s)", attr_name, target_val, src->name);
    res.num_attrs = src->num_attrs;
    for (int i = 0; i < src->num_attrs; i++) {
        strncpy(res.schema[i], src->schema[i], 64);
    }
    res.num_tuples = 0;

    int idx = relation_find_attr(src, attr_name);
    if (idx < 0) return res;

    for (int i = 0; i < src->num_tuples; i++) {
        if (strcmp(src->tuples[i].values[idx], target_val) == 0) {
            relation_add_tuple(&res, &src->tuples[i]);
        }
    }
    return res;
}

// Оператор Проекції: pi_{attrs}(R)
Relation relation_project(const Relation *src, const char attrs[][64], int num_project_attrs) {
    Relation res;
    snprintf(res.name, sizeof(res.name), "pi(%s)", src->name);
    res.num_attrs = num_project_attrs;
    res.num_tuples = 0;

    int map_idx[MAX_ATTRS];
    for (int i = 0; i < num_project_attrs; i++) {
        strncpy(res.schema[i], attrs[i], 64);
        map_idx[i] = relation_find_attr(src, attrs[i]);
    }

    for (int i = 0; i < src->num_tuples; i++) {
        Tuple proj_tuple;
        proj_tuple.count = num_project_attrs;
        for (int j = 0; j < num_project_attrs; j++) {
            if (map_idx[j] >= 0) {
                strncpy(proj_tuple.values[j], src->tuples[i].values[map_idx[j]], MAX_VAL_LEN);
            } else {
                strncpy(proj_tuple.values[j], "NULL", MAX_VAL_LEN);
            }
        }
        relation_add_tuple(&res, &proj_tuple);
    }
    return res;
}

// Оператор Природного З'єднання: R join S
Relation relation_natural_join(const Relation *r1, const Relation *r2) {
    Relation res;
    snprintf(res.name, sizeof(res.name), "(%s JOIN %s)", r1->name, r2->name);
    res.num_attrs = 0;
    res.num_tuples = 0;

    // Шукаємо спільний атрибут
    int join_r1_idx = -1, join_r2_idx = -1;
    for (int i = 0; i < r1->num_attrs; i++) {
        int idx2 = relation_find_attr(r2, r1->schema[i]);
        if (idx2 >= 0) {
            join_r1_idx = i;
            join_r2_idx = idx2;
            break;
        }
    }

    // Формуємо вихідну схему
    for (int i = 0; i < r1->num_attrs; i++) {
        strncpy(res.schema[res.num_attrs++], r1->schema[i], 64);
    }
    for (int j = 0; j < r2->num_attrs; j++) {
        if (j != join_r2_idx) {
            strncpy(res.schema[res.num_attrs++], r2->schema[j], 64);
        }
    }

    // Алгоритм вкладених петель (Nested Loop Join)
    for (int i = 0; i < r1->num_tuples; i++) {
        for (int j = 0; j < r2->num_tuples; j++) {
            bool match = (join_r1_idx < 0) || 
                         (strcmp(r1->tuples[i].values[join_r1_idx], r2->tuples[j].values[join_r2_idx]) == 0);
            if (match) {
                Tuple merged;
                merged.count = 0;
                for (int k = 0; k < r1->num_attrs; k++) {
                    strncpy(merged.values[merged.count++], r1->tuples[i].values[k], MAX_VAL_LEN);
                }
                for (int k = 0; k < r2->num_attrs; k++) {
                    if (k != join_r2_idx) {
                        strncpy(merged.values[merged.count++], r2->tuples[j].values[k], MAX_VAL_LEN);
                    }
                }
                relation_add_tuple(&res, &merged);
            }
        }
    }
    return res;
}

// Вивід відношення у консоль
void relation_print(const Relation *rel) {
    printf("=== Відношення: %s ===\n| ", rel->name);
    for (int i = 0; i < rel->num_attrs; i++) {
        printf("%-12s | ", rel->schema[i]);
    }
    printf("\n----------------------------------------\n");
    for (int i = 0; i < rel->num_tuples; i++) {
        printf("| ");
        for (int j = 0; j < rel->num_attrs; j++) {
            printf("%-12s | ", rel->tuples[i].values[j]);
        }
        printf("\n");
    }
    printf("\n");
}

int main(void) {
    Relation users = {
        .name = "Users",
        .schema = {"ID", "Name", "City"},
        .num_attrs = 3,
        .tuples = {
            {.values = {"101", "Аліса", "Київ"}, .count = 3},
            {.values = {"102", "Боб", "Львів"}, .count = 3},
            {.values = {"103", "Єва", "Київ"}, .count = 3}
        },
        .num_tuples = 3
    };

    Relation orders = {
        .name = "Orders",
        .schema = {"OrderID", "ID", "Amount"},
        .num_attrs = 3,
        .tuples = {
            {.values = {"5001", "101", "250.0"}, .count = 3},
            {.values = {"5002", "101", "120.0"}, .count = 3},
            {.values = {"5003", "102", "890.0"}, .count = 3}
        },
        .num_tuples = 3
    };

    relation_print(&users);
    relation_print(&orders);

    // 1. Селекція: σ_{City = 'Київ'}(Users)
    Relation kyiv_users = relation_select(&users, "City", "Київ");
    relation_print(&kyiv_users);

    // 2. Природне з'єднання: Users ⋈ Orders
    Relation joined = relation_natural_join(&users, &orders);
    relation_print(&joined);

    // 3. Проекція: π_{Name, Amount}(Users ⋈ Orders)
    char proj_cols[2][64] = {"Name", "Amount"};
    Relation result = relation_project(&joined, proj_cols, 2);
    relation_print(&result);

    return 0;
}
