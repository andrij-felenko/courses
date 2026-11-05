#include <stdio.h>
#include <stdlib.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdbool.h>

typedef struct Node {
    int value;
    struct Node* next;
} Node;

typedef struct {
    Node* ptr;
    uintptr_t tag;
} TaggedPointer;

_Atomic TaggedPointer stack_head;

void init_stack(void) {
    TaggedPointer init_tp = { .ptr = NULL, .tag = 0 };
    atomic_store(&stack_head, init_tp);
}

void push(int val) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->value = val;
    TaggedPointer old_head = atomic_load(&stack_head);
    TaggedPointer new_head;
    do {
        new_node->next = old_head.ptr;
        new_head.ptr = new_node;
        new_head.tag = old_head.tag + 1;
    } while (!atomic_compare_exchange_weak(&stack_head, &old_head, new_head));
}

bool pop(int* val) {
    TaggedPointer old_head = atomic_load(&stack_head);
    TaggedPointer new_head;
    do {
        if (old_head.ptr == NULL) return false;
        new_head.ptr = old_head.ptr->next;
        new_head.tag = old_head.tag + 1;
    } while (!atomic_compare_exchange_weak(&stack_head, &old_head, new_head));

    *val = old_head.ptr->value;
    free(old_head.ptr);
    return true;
}

int main(void) {
    printf("=== Treiber Stack ABA Tagged Pointer Protection (C) ===\n");
    init_stack();
    push(42);
    push(84);
    int v;
    if (pop(&v)) printf("Popped: %d\n", v);
    if (pop(&v)) printf("Popped: %d\n", v);
    return 0;
}
