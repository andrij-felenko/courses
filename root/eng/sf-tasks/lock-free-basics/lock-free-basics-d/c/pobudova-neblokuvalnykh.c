#include <stdatomic.h>
#include <stdbool.h>
#include <stdlib.h>

typedef struct Node {
    int value;
    struct Node* next;
} Node;

typedef struct {
    _Atomic(Node*) head;
} TreiberStack;

void stack_init(TreiberStack* stack) {
    atomic_init(&stack->head, NULL);
}

void stack_push(TreiberStack* stack, int value) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->value = value;

    // Зчитуємо поточну вершину
    Node* old_head = atomic_load_explicit(&stack->head, memory_order_relaxed);

    // Оптимістичний цикл CAS
    do {
        new_node->next = old_head;
        // memory_order_release гарантує, що ініціалізація полів вузла
        // стане видимою іншим ядрам до того, як оновиться покажчик head
    } while (!atomic_compare_exchange_weak_explicit(
        &stack->head,
        &old_head,
        new_node,
        memory_order_release,
        memory_order_relaxed));
}

bool stack_pop(TreiberStack* stack, int* result) {
    // memory_order_acquire гарантує коректне отримання полів вузла
    Node* old_head = atomic_load_explicit(&stack->head, memory_order_acquire);

    while (old_head != NULL) {
        Node* next_node = old_head->next;

        if (atomic_compare_exchange_weak_explicit(
                &stack->head,
                &old_head,
                next_node,
                memory_order_acquire,
                memory_order_relaxed)) {
            *result = old_head->value;
            // Увага: фізичне видалення потребує безпечного керування пам'яттю
            free(old_head);
            return true;
        }
    }
    return false; // Стек порожній
}
