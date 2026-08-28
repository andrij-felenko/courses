#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <float.h>
#include <math.h>

#define RTREE_MAX_ENTRIES 4
#define RTREE_MIN_ENTRIES 2

typedef struct {
    double min_x, min_y;
    double max_x, max_y;
} Box2D;

typedef struct {
    double x, y;
} Point2D;

typedef struct RTreeNode RTreeNode;

typedef struct {
    Box2D box;
    union {
        RTreeNode* child;
        long long id;
    } target;
} RTreeEntry;

struct RTreeNode {
    bool is_leaf;
    int count;
    RTreeEntry entries[RTREE_MAX_ENTRIES + 1];
};

typedef struct {
    RTreeNode* root;
} RTree;

/* Геометричні примітиви */

static inline Box2D box_create(double x1, double y1, double x2, double y2) {
    Box2D b = { x1 < x2 ? x1 : x2, y1 < y2 ? y1 : y2,
                x1 > x2 ? x1 : x2, y1 > y2 ? y1 : y2 };
    return b;
}

static inline double box_area(const Box2D* b) {
    return (b->max_x - b->min_x) * (b->max_y - b->min_y);
}

static inline Box2D box_combine(const Box2D* a, const Box2D* b) {
    Box2D res;
    res.min_x = a->min_x < b->min_x ? a->min_x : b->min_x;
    res.min_y = a->min_y < b->min_y ? a->min_y : b->min_y;
    res.max_x = a->max_x > b->max_x ? a->max_x : b->max_x;
    res.max_y = a->max_y > b->max_y ? a->max_y : b->max_y;
    return res;
}

static inline double box_enlargement(const Box2D* base, const Box2D* add) {
    Box2D combined = box_combine(base, add);
    return box_area(&combined) - box_area(base);
}

static inline bool box_intersects(const Box2D* a, const Box2D* b) {
    return (a->min_x <= b->max_x && a->max_x >= b->min_x &&
            a->min_y <= b->max_y && a->max_y >= b->min_y);
}

static inline double point_mindist_sq(const Point2D* p, const Box2D* b) {
    double dx = 0.0, dy = 0.0;
    if (p->x < b->min_x) dx = b->min_x - p->x;
    else if (p->x > b->max_x) dx = p->x - b->max_x;
    if (p->y < b->min_y) dy = b->min_y - p->y;
    else if (p->y > b->max_y) dy = p->y - b->max_y;
    return dx * dx + dy * dy;
}

/* Створення та очищення вузлів */

static RTreeNode* node_create(bool is_leaf) {
    RTreeNode* n = (RTreeNode*)malloc(sizeof(RTreeNode));
    if (!n) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }
    n->is_leaf = is_leaf;
    n->count = 0;
    return n;
}

static void node_free(RTreeNode* node) {
    if (!node) return;
    if (!node->is_leaf) {
        for (int i = 0; i < node->count; ++i) {
            node_free(node->entries[i].target.child);
        }
    }
    free(node);
}

static Box2D node_cover(const RTreeNode* node) {
    if (node->count == 0) return box_create(0, 0, 0, 0);
    Box2D res = node->entries[0].box;
    for (int i = 1; i < node->count; ++i) {
        res = box_combine(&res, &node->entries[i].box);
    }
    return res;
}

/* Алгоритм квадратичного розщеплення Гутмана */

static void split_node(RTreeNode* old_node, RTreeNode* new_node) {
    int total = old_node->count;
    RTreeEntry all[RTREE_MAX_ENTRIES + 1];
    for (int i = 0; i < total; ++i) all[i] = old_node->entries[i];

    /* 1. PickSeeds: знаходження пари з максимальною мертвою площею */
    int seed1 = 0, seed2 = 1;
    double max_d = -1.0;
    for (int i = 0; i < total; ++i) {
        for (int j = i + 1; j < total; ++j) {
            Box2D u = box_combine(&all[i].box, &all[j].box);
            double d = box_area(&u) - box_area(&all[i].box) - box_area(&all[j].box);
            if (d > max_d) {
                max_d = d;
                seed1 = i;
                seed2 = j;
            }
        }
    }

    bool taken[RTREE_MAX_ENTRIES + 1] = { false };
    taken[seed1] = true;
    taken[seed2] = true;

    old_node->count = 0;
    new_node->count = 0;
    new_node->is_leaf = old_node->is_leaf;

    old_node->entries[old_node->count++] = all[seed1];
    new_node->entries[new_node->count++] = all[seed2];

    Box2D box1 = all[seed1].box;
    Box2D box2 = all[seed2].box;
    int assigned = 2;

    /* 2. Розподіл решти елементів */
    while (assigned < total) {
        /* Перевірка умови мінімальної наповненості m */
        if (old_node->count + (total - assigned) == RTREE_MIN_ENTRIES) {
            for (int i = 0; i < total; ++i) {
                if (!taken[i]) {
                    old_node->entries[old_node->count++] = all[i];
                    taken[i] = true;
                    assigned++;
                }
            }
            break;
        }
        if (new_node->count + (total - assigned) == RTREE_MIN_ENTRIES) {
            for (int i = 0; i < total; ++i) {
                if (!taken[i]) {
                    new_node->entries[new_node->count++] = all[i];
                    taken[i] = true;
                    assigned++;
                }
            }
            break;
        }

        /* PickNext: вибір елемента з найбільшим контрастом розширення */
        int best_idx = -1;
        double max_diff = -1.0;
        for (int i = 0; i < total; ++i) {
            if (taken[i]) continue;
            double d1 = box_enlargement(&box1, &all[i].box);
            double d2 = box_enlargement(&box2, &all[i].box);
            double diff = fabs(d1 - d2);
            if (diff > max_diff) {
                max_diff = diff;
                best_idx = i;
            }
        }

        double d1 = box_enlargement(&box1, &all[best_idx].box);
        double d2 = box_enlargement(&box2, &all[best_idx].box);

        if (d1 < d2 || (d1 == d2 && box_area(&box1) < box_area(&box2)) ||
           (d1 == d2 && box_area(&box1) == box_area(&box2) && old_node->count <= new_node->count)) {
            old_node->entries[old_node->count++] = all[best_idx];
            box1 = box_combine(&box1, &all[best_idx].box);
        } else {
            new_node->entries[new_node->count++] = all[best_idx];
            box2 = box_combine(&box2, &all[best_idx].box);
        }
        taken[best_idx] = true;
        assigned++;
    }
}

/* Рекурсивна вставка */

static RTreeNode* insert_recursive(RTreeNode* node, const RTreeEntry* entry) {
    if (node->is_leaf) {
        node->entries[node->count++] = *entry;
    } else {
        /* ChooseLeaf евристика: обираємо дочірній вузол із найменшим розширенням */
        int best_idx = 0;
        double min_enl = box_enlargement(&node->entries[0].box, &entry->box);
        double min_area = box_area(&node->entries[0].box);

        for (int i = 1; i < node->count; ++i) {
            double enl = box_enlargement(&node->entries[i].box, &entry->box);
            double a = box_area(&node->entries[i].box);
            if (enl < min_enl || (enl == min_enl && a < min_area)) {
                min_enl = enl;
                min_area = a;
                best_idx = i;
            }
        }

        RTreeNode* split_child = insert_recursive(node->entries[best_idx].target.child, entry);
        node->entries[best_idx].box = node_cover(node->entries[best_idx].target.child);

        if (split_child) {
            RTreeEntry new_entry;
            new_entry.box = node_cover(split_child);
            new_entry.target.child = split_child;
            node->entries[node->count++] = new_entry;
        }
    }

    if (node->count > RTREE_MAX_ENTRIES) {
        RTreeNode* new_sibling = node_create(node->is_leaf);
        split_node(node, new_sibling);
        return new_sibling;
    }
    return NULL;
}

void rtree_insert(RTree* tree, Box2D box, long long id) {
    RTreeEntry entry;
    entry.box = box;
    entry.target.id = id;

    if (!tree->root) {
        tree->root = node_create(true);
        tree->root->entries[tree->root->count++] = entry;
        return;
    }

    RTreeNode* split_root = insert_recursive(tree->root, &entry);
    if (split_root) {
        RTreeNode* new_root = node_create(false);
        new_root->entries[0].box = node_cover(tree->root);
        new_root->entries[0].target.child = tree->root;
        new_root->entries[1].box = node_cover(split_root);
        new_root->entries[1].target.child = split_root;
        new_root->count = 2;
        tree->root = new_root;
    }
}

/* Віконний пошук */

static void search_recursive(const RTreeNode* node, const Box2D* query, void (*callback)(long long id, void* ctx), void* ctx) {
    for (int i = 0; i < node->count; ++i) {
        if (box_intersects(&node->entries[i].box, query)) {
            if (node->is_leaf) {
                callback(node->entries[i].target.id, ctx);
            } else {
                search_recursive(node->entries[i].target.child, query, callback, ctx);
            }
        }
    }
}

void rtree_search(const RTree* tree, Box2D query, void (*callback)(long long id, void* ctx), void* ctx) {
    if (tree->root) {
        search_recursive(tree->root, &query, callback, ctx);
    }
}

static void collect_results(long long id, void* ctx) {
    int* count = (int*)ctx;
    (*count)++;
    printf("Знайдено об'єкт id: %lld\n", id);
}

int main(void) {
    RTree tree = { NULL };

    /* Вставка 6 тестових геометричних об'єктів */
    rtree_insert(&tree, box_create(10, 10, 20, 20), 101);
    rtree_insert(&tree, box_create(15, 12, 25, 22), 102);
    rtree_insert(&tree, box_create(50, 60, 70, 80), 103);
    rtree_insert(&tree, box_create(55, 62, 75, 85), 104);
    rtree_insert(&tree, box_create(12, 14, 22, 24), 105);
    rtree_insert(&tree, box_create(80, 80, 90, 90), 106);

    printf("=== Віконний пошук у зоні [5, 5]x[30, 30] ===\n");
    int found = 0;
    rtree_search(&tree, box_create(5, 5, 30, 30), collect_results, &found);
    printf("Всього знайдено: %d об'єктів\n", found);

    node_free(tree.root);
    return 0;
}
