#include <stdatomic.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

typedef struct {
    Node* ptr;
    uint64_t tag;
} TaggedNodePtr;

typedef struct {
    _Atomic TaggedNodePtr head;
} TaggedStack;

void tagged_stack_init(TaggedStack* stack) {
    TaggedNodePtr init_val = {NULL, 0};
    atomic_store_explicit(&stack->head, init_val, memory_order_relaxed);
}

void tagged_stack_push(TaggedStack* stack, int val) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->data = val;

    TaggedNodePtr current = atomic_load_explicit(&stack->head, memory_order_relaxed);
    TaggedNodePtr next_tagged;

    do {
        new_node->next = current.ptr;
        next_tagged.ptr = new_node;
        next_tagged.tag = current.tag + 1;
    } while (!atomic_compare_exchange_weak_explicit(
        &stack->head, &current, next_tagged,
        memory_order_release, memory_order_relaxed));
}

bool tagged_stack_pop(TaggedStack* stack, int* result) {
    TaggedNodePtr current = atomic_load_explicit(&stack->head, memory_order_acquire);
    TaggedNodePtr next_tagged;

    do {
        if (current.ptr == NULL) {
            return false;
        }
        next_tagged.ptr = current.ptr->next;
        next_tagged.tag = current.tag + 1;
    } while (!atomic_compare_exchange_weak_explicit(
        &stack->head, &current, next_tagged,
        memory_order_acq_rel, memory_order_acquire));

    *result = current.ptr->data;
    return true;
}
