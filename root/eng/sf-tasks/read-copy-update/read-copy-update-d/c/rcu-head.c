#include <stdio.h>
#include <stdlib.h>
#include <stdatomic.h>
#include <stdbool.h>

// Структура вузла з вбудованим заголовком утилізації RCU
struct rcu_head {
    void (*func)(struct rcu_head *head);
    struct rcu_head *next;
};

struct node {
    int key;
    int value;
    struct node *_Atomic next;
    struct rcu_head rcu;
};

// Загальний головний вказівник списку
struct node *_Atomic list_head = NULL;

// Спеціальний макрос читання вказівника із семантикою load-consume/acquire
#define rcu_dereference(p) atomic_load_explicit(&(p), memory_order_consume)

// Спеціальний макрос публікації вказівника із семантикою store-release
#define rcu_assign_pointer(p, v) atomic_store_explicit(&(p), (v), memory_order_release)

// Пошук у списку під захистом RCU-читацького контексту
bool rcu_list_search(int key, int *out_value) {
    // Вхід у критичну секцію читання RCU
    struct node *curr = rcu_dereference(list_head);
    
    while (curr != NULL) {
        if (curr->key == key) {
            *out_value = curr->value;
            // Успішно знайдено без використання замків
            return true;
        }
        curr = rcu_dereference(curr->next);
    }
    return false;
}

// Вставка нового вузла в початок списку
void rcu_list_insert(int key, int value) {
    struct node *new_node = malloc(sizeof(struct node));
    new_node->key = key;
    new_node->value = value;
    
    // Ініціалізація зв'язку з поточним головою списку
    struct node *old_head = atomic_load_explicit(&list_head, memory_order_relaxed);
    do {
        atomic_store_explicit(&new_node->next, old_head, memory_order_relaxed);
    // Атомарна підміна голови списку із семантикою release
    } while (!atomic_compare_exchange_weak_explicit(
                &list_head, &old_head, new_node,
                memory_order_release, memory_order_relaxed));
}

// Callback для асинхронної утилізації пам'яті
static void free_node_rcu_callback(struct rcu_head *head) {
    struct node *n = (struct node *)((char *)head - offsetof(struct node, rcu));
    free(n);
}

// Асинхронне вивільнення вузла через імітацію call_rcu
void rcu_reclaim_node_async(struct node *n) {
    n->rcu.func = free_node_rcu_callback;
    // Реєстрація утилізації після проходження періоду відстрочки
    // В дійсних системних середовищах викликом є call_rcu(&n->rcu, free_node_rcu_callback);
    n->rcu.func(&n->rcu);
}
