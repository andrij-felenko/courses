#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

/* Структура 1D інтервалу [low, high] */
typedef struct Interval {
    double low;
    double high;
} Interval;

/* Структура вузла доповненого інтервального дерева */
typedef struct IntervalNode {
    Interval interval;
    double max_high;
    struct IntervalNode* left;
    struct IntervalNode* right;
} IntervalNode;

/* Створення нового інтервалу */
Interval create_interval(double low, double high) {
    Interval it = {low, high};
    return it;
}

/* Перевірка перетину двох інтервалів [a.low, a.high] та [b.low, b.high] */
bool intervals_overlap(Interval a, Interval b) {
    return (a.low <= b.high) && (a.high >= b.low);
}

/* Допоміжна функція знаходження максимуму з двох чисел */
static inline double max_double(double a, double b) {
    return (a > b) ? a : b;
}

/* Створення нового вузла дерева у динамічній пам'яті */
IntervalNode* create_node(Interval it) {
    IntervalNode* node = (IntervalNode*)malloc(sizeof(IntervalNode));
    if (!node) {
        perror("Помилка виділення пам'яті для IntervalNode");
        exit(EXIT_FAILURE);
    }
    node->interval = it;
    node->max_high = it.high;
    node->left = NULL;
    node->right = NULL;
    return node;
}

/* Перерахунок атрибута max_high на основі значень дочірніх вузлів */
void update_node_max(IntervalNode* node) {
    if (!node) return;
    
    double current_max = node->interval.high;
    if (node->left && node->left->max_high > current_max) {
        current_max = node->left->max_high;
    }
    if (node->right && node->right->max_high > current_max) {
        current_max = node->right->max_high;
    }
    node->max_high = current_max;
}

/* Рекурсивна вставка нового інтервалу у дерево (BST за ключем low) */
IntervalNode* interval_insert(IntervalNode* root, Interval it) {
    /* Базовий випадок: порожнє піддерево */
    if (root == NULL) {
        return create_node(it);
    }
    
    /* Ключем впорядкування у BST є ліва межа low */
    if (it.low < root->interval.low) {
        root->left = interval_insert(root->left, it);
    } else {
        root->right = interval_insert(root->right, it);
    }
    
    /* Оновлення max_high на зворотному шляху рекурсії */
    update_node_max(root);
    
    return root;
}

/* Пошук одного інтервалу, що перетинається з query */
IntervalNode* interval_search(IntervalNode* root, Interval query) {
    IntervalNode* current = root;
    
    while (current != NULL && !intervals_overlap(current->interval, query)) {
        /* Якщо лівий син існує і його max_high >= query.low,
           гарантовано перетинаючий інтервал є у лівому піддереві */
        if (current->left != NULL && current->left->max_high >= query.low) {
            current = current->left;
        } else {
            current = current->right;
        }
    }
    
    return current;
}

/* Динамічний масив для збереження списку результатів */
typedef struct NodeList {
    IntervalNode** data;
    size_t capacity;
    size_t size;
} NodeList;

NodeList* create_node_list(size_t initial_capacity) {
    NodeList* list = (NodeList*)malloc(sizeof(NodeList));
    list->capacity = initial_capacity;
    list->size = 0;
    list->data = (IntervalNode**)malloc(initial_capacity * sizeof(IntervalNode*));
    return list;
}

void list_append(NodeList* list, IntervalNode* node) {
    if (list->size >= list->capacity) {
        list->capacity *= 2;
        list->data = (IntervalNode**)realloc(list->data, list->capacity * sizeof(IntervalNode*));
    }
    list->data[list->size++] = node;
}

void free_node_list(NodeList* list) {
    if (list) {
        free(list->data);
        free(list);
    }
}

/* Рекурсивний пошук усіх перетинів із запитом query */
void interval_search_all_recursive(IntervalNode* root, Interval query, NodeList* results) {
    if (root == NULL) return;
    
    /* 1. Перевірка перетину у поточному вузлі */
    if (intervals_overlap(root->interval, query)) {
        list_append(results, root);
    }
    
    /* 2. Похід у ліве піддерево, якщо max_high лівого сина охоплює query.low */
    if (root->left != NULL && root->left->max_high >= query.low) {
        interval_search_all_recursive(root->left, query, results);
    }
    
    /* 3. Похід у праве піддерево, якщо можливий перетин праворуч */
    if (root->right != NULL && root->interval.low <= query.high && root->right->max_high >= query.low) {
        interval_search_all_recursive(root->right, query, results);
    }
}

/* Звільнення всієї пам'яті дерева (Post-order traversal) */
void free_interval_tree(IntervalNode* root) {
    if (root == NULL) return;
    free_interval_tree(root->left);
    free_interval_tree(root->right);
    free(root);
}

/* Демонстраційна програма */
int main(void) {
    IntervalNode* root = NULL;
    
    Interval intervals[] = {
        {15, 20},
        {10, 30},
        {17, 19},
        {5, 20},
        {12, 15},
        {30, 40}
    };
    size_t n = sizeof(intervals) / sizeof(intervals[0]);
    
    printf("=== Побудова інтервального дерева (C) ===\n");
    for (size_t i = 0; i < n; ++i) {
        root = interval_insert(root, intervals[i]);
        printf("Вставлено: [%g, %g]\n", intervals[i].low, intervals[i].high);
    }
    
    printf("\nЗагальний max_high кореня: %g\n", root->max_high);
    
    /* Одиничний пошук перетину для Q = [21, 23] */
    Interval query1 = {21, 23};
    printf("\nПошук одиничного перетину для Q = [%g, %g]:\n", query1.low, query1.high);
    IntervalNode* match = interval_search(root, query1);
    if (match) {
        printf("Знайдено збіг: [%g, %g] (max_high = %g)\n", 
               match->interval.low, match->interval.high, match->max_high);
    } else {
        printf("Перетинів не знайдено.\n");
    }
    
    /* Пошук усіх перетинів для Q = [14, 18] */
    Interval query2 = {14, 18};
    printf("\nПошук усіх перетинів для Q = [%g, %g]:\n", query2.low, query2.high);
    NodeList* all_matches = create_node_list(4);
    interval_search_all_recursive(root, query2, all_matches);
    
    printf("Знайдено %zu перетинів:\n", all_matches->size);
    for (size_t i = 0; i < all_matches->size; ++i) {
        printf(" - [%g, %g]\n", all_matches->data[i]->interval.low, all_matches->data[i]->interval.high);
    }
    
    free_node_list(all_matches);
    free_interval_tree(root);
    printf("\nПам'ять успішно звільнено.\n");
    return 0;
}
