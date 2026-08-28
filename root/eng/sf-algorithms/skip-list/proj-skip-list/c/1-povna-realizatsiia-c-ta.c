#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define SKIPLIST_MAX_LEVEL 32
#define SKIPLIST_P_FACTOR 4  /* p = 1/4 */

typedef struct SkipNode {
    int key;
    int value;
    int level;
    struct SkipNode* forward[];  /* Гнучкий масив покажчиків */
} SkipNode;

typedef struct SkipList {
    int level;          /* Поточний максимальний активний рівень */
    size_t size;        /* Загальна кількість збережених пар */
    SkipNode* head;     /* Головний вартовий вузол */
} SkipList;

/* Створення нового вузла єдиним блоком виділення пам'яті */
static SkipNode* create_node(int level, int key, int value) {
    size_t total_size = sizeof(SkipNode) + sizeof(SkipNode*) * (size_t)level;
    SkipNode* node = (SkipNode*)malloc(total_size);
    if (!node) return NULL;
    node->key = key;
    node->value = value;
    node->level = level;
    for (int i = 0; i < level; i++) {
        node->forward[i] = NULL;
    }
    return node;
}

/* Ініціалізація нового пропускного списку */
SkipList* skiplist_create(void) {
    SkipList* list = (SkipList*)malloc(sizeof(SkipList));
    if (!list) return NULL;
    list->level = 1;
    list->size = 0;
    list->head = create_node(SKIPLIST_MAX_LEVEL, 0, 0);
    if (!list->head) {
        free(list);
        return NULL;
    }
    return list;
}

/* Швидкий генератор випадкових чисел XORShift для уникнення накладних витрат rand() */
static uint32_t xorshift32_state = 2463534242U;
static uint32_t fast_rand(void) {
    uint32_t x = xorshift32_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    xorshift32_state = x;
    return x;
}

/* Генерація випадкового рівня з геометричним розподілом p = 1/4 */
static int random_level(void) {
    int lvl = 1;
    while ((fast_rand() & (SKIPLIST_P_FACTOR - 1)) == 0 && lvl < SKIPLIST_MAX_LEVEL) {
        lvl++;
    }
    return lvl;
}

/* Пошук значення за ключем */
bool skiplist_search(const SkipList* list, int key, int* out_value) {
    if (!list) return false;
    SkipNode* current = list->head;

    /* Спуск зверху вниз від найвищого активного рівня до нульового */
    for (int i = list->level - 1; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->key < key) {
            current = current->forward[i];
        }
    }

    current = current->forward[0];

    if (current != NULL && current->key == key) {
        if (out_value) *out_value = current->value;
        return true;
    }
    return false;
}

/* Вставка ключа і значення (перезапис значення, якщо ключ уже існує) */
bool skiplist_insert(SkipList* list, int key, int value) {
    if (!list) return false;
    SkipNode* update[SKIPLIST_MAX_LEVEL];
    SkipNode* current = list->head;

    /* 1. Пошук позиції та збереження попередників на кожному рівні */
    for (int i = list->level - 1; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->key < key) {
            current = current->forward[i];
        }
        update[i] = current;
    }

    current = current->forward[0];

    /* Якщо ключ уже існує — оновлюємо значення без зміни форми списку */
    if (current != NULL && current->key == key) {
        current->value = value;
        return true;
    }

    /* 2. Вибір випадкового рівня для нового елемента */
    int new_level = random_level();

    /* Якщо новий рівень перевищує поточний — оновлюємо верхівку масиву update */
    if (new_level > list->level) {
        for (int i = list->level; i < new_level; i++) {
            update[i] = list->head;
        }
        list->level = new_level;
    }

    /* 3. Створення вузла та локальне перечіплення покажчиків */
    SkipNode* new_node = create_node(new_level, key, value);
    if (!new_node) return false;

    for (int i = 0; i < new_level; i++) {
        new_node->forward[i] = update[i]->forward[i];
        update[i]->forward[i] = new_node;
    }

    list->size++;
    return true;
}

/* Видалення ключа зі списку */
bool skiplist_delete(SkipList* list, int key) {
    if (!list) return false;
    SkipNode* update[SKIPLIST_MAX_LEVEL];
    SkipNode* current = list->head;

    /* 1. Фіксація попередників */
    for (int i = list->level - 1; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->key < key) {
            current = current->forward[i];
        }
        update[i] = current;
    }

    current = current->forward[0];

    if (current == NULL || current->key != key) {
        return false;
    }

    /* 2. Перечіплення покажчиків в обхід видаленого вузла */
    for (int i = 0; i < list->level; i++) {
        if (update[i]->forward[i] != current) {
            break;
        }
        update[i]->forward[i] = current->forward[i];
    }

    free(current);

    /* 3. Коригування висоти списку при видаленні найвищого вузла */
    while (list->level > 1 && list->head->forward[list->level - 1] == NULL) {
        list->level--;
    }

    list->size--;
    return true;
}

/* Діапазонне сканування з функцією зворотного виклику */
void skiplist_range(const SkipList* list, int min_key, int max_key,
                    void (*callback)(int k, int v, void* ctx), void* ctx) {
    if (!list || !callback) return;
    SkipNode* current = list->head;

    for (int i = list->level - 1; i >= 0; i--) {
        while (current->forward[i] != NULL && current->forward[i]->key < min_key) {
            current = current->forward[i];
        }
    }

    current = current->forward[0];
    while (current != NULL && current->key <= max_key) {
        callback(current->key, current->value, ctx);
        current = current->forward[0];
    }
}

/* Повне звільнення всіх виділених ресурсів */
void skiplist_destroy(SkipList* list) {
    if (!list) return;
    SkipNode* current = list->head->forward[0];
    while (current != NULL) {
        SkipNode* next = current->forward[0];
        free(current);
        current = next;
    }
    free(list->head);
    free(list);
}
