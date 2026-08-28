#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <stdbool.h>

// Вузол біноміального дерева
typedef struct BinomialNode {
    int key;
    int degree;
    struct BinomialNode *parent;
    struct BinomialNode *child;
    struct BinomialNode *sibling;
} BinomialNode;

// Створення нового вузла
BinomialNode* node_create(int key) {
    BinomialNode* node = (BinomialNode*)malloc(sizeof(BinomialNode));
    if (!node) return NULL;
    node->key = key;
    node->degree = 0;
    node->parent = NULL;
    node->child = NULL;
    node->sibling = NULL;
    return node;
}

// Зв'язування двох дерев B_k з утворенням B_{k+1}
// Вузол y робиться дитиною вузла z (припускається z->key <= y->key)
static void binomial_link(BinomialNode* y, BinomialNode* z) {
    y->parent = z;
    y->sibling = z->child;
    z->child = y;
    z->degree++;
}

// Злиття двох відсортованих списків коренів за зростанням степеня (як у MergeSort)
static BinomialNode* merge_root_lists(BinomialNode* h1, BinomialNode* h2) {
    if (!h1) return h2;
    if (!h2) return h1;

    BinomialNode* head = NULL;
    BinomialNode** tail = &head;

    while (h1 && h2) {
        if (h1->degree <= h2->degree) {
            *tail = h1;
            h1 = h1->sibling;
        } else {
            *tail = h2;
            h2 = h2->sibling;
        }
        tail = &((*tail)->sibling);
    }
    *tail = h1 ? h1 : h2;
    return head;
}

// Основна операція: об'єднання двох біноміальних куп
BinomialNode* binomial_heap_union(BinomialNode* h1, BinomialNode* h2) {
    BinomialNode* head = merge_root_lists(h1, h2);
    if (!head) return NULL;

    BinomialNode* prev = NULL;
    BinomialNode* curr = head;
    BinomialNode* next = curr->sibling;

    while (next) {
        // Випадок 1 і 2: степені різні АБО три послідовні дерева мають одинаковий степінь
        if ((curr->degree != next->degree) ||
            (next->sibling && next->sibling->degree == curr->degree)) {
            prev = curr;
            curr = next;
        } else {
            // Випадок 3 і 4: однакові степені — об'єднуємо у відповідну сторону
            if (curr->key <= next->key) {
                curr->sibling = next->sibling;
                binomial_link(next, curr);
            } else {
                if (!prev) {
                    head = next;
                } else {
                    prev->sibling = next;
                }
                binomial_link(curr, next);
                curr = next;
            }
        }
        next = curr->sibling;
    }
    return head;
}

// Вставка нового ключа у купу
BinomialNode* binomial_heap_insert(BinomialNode* heap, int key) {
    BinomialNode* temp = node_create(key);
    return binomial_heap_union(heap, temp);
}

// Пошук вузла з мінімальним ключем серед коренів
BinomialNode* binomial_heap_find_min(BinomialNode* heap) {
    if (!heap) return NULL;
    BinomialNode* min_node = heap;
    BinomialNode* curr = heap->sibling;
    while (curr) {
        if (curr->key < min_node->key) {
            min_node = curr;
        }
        curr = curr->sibling;
    }
    return min_node;
}

// Допоміжна функція розвороту списку дітей
static BinomialNode* reverse_list(BinomialNode* node) {
    BinomialNode* prev = NULL;
    BinomialNode* curr = node;
    while (curr) {
        BinomialNode* next = curr->sibling;
        curr->sibling = prev;
        curr->parent = NULL; // Корені нової купи не мають батька
        prev = curr;
        curr = next;
    }
    return prev;
}

// Вилучення мінімального ключа з купи
BinomialNode* binomial_heap_extract_min(BinomialNode* heap, int* out_min_key) {
    if (!heap) return NULL;

    // 1. Знаходимо мінімальний корінь та його попередника у списку
    BinomialNode* min_node = heap;
    BinomialNode* min_prev = NULL;

    BinomialNode* curr = heap;
    BinomialNode* prev = NULL;

    while (curr) {
        if (curr->key < min_node->key) {
            min_node = curr;
            min_prev = prev;
        }
        prev = curr;
        curr = curr->sibling;
    }

    if (out_min_key) *out_min_key = min_node->key;

    // 2. Вилучаємо min_node зі списку коренів
    if (min_prev) {
        min_prev->sibling = min_node->sibling;
    } else {
        heap = min_node->sibling;
    }

    // 3. Розвертаємо список дітей min_node, утворюючи нову купу
    BinomialNode* child_heap = reverse_list(min_node->child);
    free(min_node);

    // 4. Об'єднуємо залишок купи з новою купою дітей
    return binomial_heap_union(heap, child_heap);
}

// Зменшення ключа вузла
void binomial_heap_decrease_key(BinomialNode* node, int new_key) {
    if (!node || new_key > node->key) return;

    node->key = new_key;
    BinomialNode* curr = node;
    BinomialNode* parent = curr->parent;

    // Просіювання вгору (sift-up)
    while (parent && curr->key < parent->key) {
        // Обмін значеннями ключів
        int temp = curr->key;
        curr->key = parent->key;
        parent->key = temp;

        curr = parent;
        parent = curr->parent;
    }
}

// Рекурсивне звільнення пам'яті купи
void binomial_heap_free(BinomialNode* heap) {
    while (heap) {
        BinomialNode* sibling = heap->sibling;
        if (heap->child) {
            binomial_heap_free(heap->child);
        }
        free(heap);
        heap = sibling;
    }
}
