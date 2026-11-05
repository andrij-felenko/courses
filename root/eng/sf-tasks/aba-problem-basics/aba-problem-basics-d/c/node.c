/* Реалізація безблокувального стеку із захистом від ABA на C11 */
#include <stdatomic.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdbool.h>

// Вузол стеку
typedef struct Node {
    int data;
    struct Node* next;
} Node;

// Тегований вказівник з вирівнюванням на 16 байт для 128-бітного атомарного CAS
typedef struct alignas(16) TaggedPointer {
    Node* ptr;
    uintptr_t tag;
} TaggedPointer;

typedef struct TreiberStack {
    _Atomic TaggedPointer head;
} TreiberStack;

void stack_init(TreiberStack* stack) {
    TaggedPointer init_val = { .ptr = NULL, .tag = 0 };
    atomic_init(&stack->head, init_val);
}

void stack_push(TreiberStack* stack, int value) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->data = value;

    TaggedPointer old_head = atomic_load(&stack->head);
    TaggedPointer new_head;

    do {
        new_node->next = old_head.ptr;
        new_head.ptr = new_node;
        new_head.tag = old_head.tag + 1; // Атомарне прирощення тегу версії
    } while (!atomic_compare_exchange_weak(&stack->head, &old_head, new_head));
}

bool stack_pop(TreiberStack* stack, int* result) {
    TaggedPointer old_head = atomic_load(&stack->head);
    TaggedPointer new_head;

    do {
        if (old_head.ptr == NULL) {
            return false; // Стек порожній
        }
        new_head.ptr = old_head.ptr->next;
        new_head.tag = old_head.tag + 1; // Інкремент версії при вилученні
    } while (!atomic_compare_exchange_weak(&stack->head, &old_head, new_head));

    *result = old_head.ptr->data;
    // Звільнення пам'яті (у виробничих системах поєднується з Hazard Pointers)
    free(old_head.ptr);
    return true;
}
