#include <stdatomic.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

typedef struct {
    _Atomic(Node*) top;
} LockFreeStack;

void stack_init(LockFreeStack* stack) {
    atomic_init(&stack->top, NULL);
}

bool stack_pop(LockFreeStack* stack, int* result) {
    Node* old_top = atomic_load_explicit(&stack->top, memory_order_acquire);
    while (old_top != NULL) {
        // КРОК 1: Збереження наступного вузла до атомарного обміну
        Node* next_node = old_top->next;

        // Якщо інший потік видалить old_top та повторно виділить цю ж адресу,
        // atomic_compare_exchange_weak повернутиме true за хибним збігом адрес!
        if (atomic_compare_exchange_weak_explicit(&stack->top, &old_top, next_node,
                                                  memory_order_release,
                                                  memory_order_acquire)) {
            *result = old_top->data;
            free(old_top);
            return true;
        }
    }
    return false;
}
