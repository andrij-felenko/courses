#include <stdio.h>
#include <stdlib.h>
#include <stdatomic.h>
#include <stdbool.h>

typedef struct Node {
    int data;
    struct Node* next;
} Node;

_Atomic(Node*) stack_head = NULL;

void push(int val) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->data = val;
    Node* old_head = atomic_load_explicit(&stack_head, memory_order_relaxed);
    do {
        new_node->next = old_head;
    } while (!atomic_compare_exchange_weak_explicit(
        &stack_head, &old_head, new_node, memory_order_release, memory_order_relaxed));
}

bool pop(int* val) {
    Node* old_head = atomic_load_explicit(&stack_head, memory_order_acquire);
    do {
        if (!old_head) return false;
    } while (!atomic_compare_exchange_weak_explicit(
        &stack_head, &old_head, old_head->next, memory_order_release, memory_order_relaxed));

    *val = old_head->data;
    free(old_head);
    return true;
}

int main(void) {
    printf("=== CAS Atomic Lock-Free Stack (C) ===\n");
    push(10);
    push(20);
    push(30);

    int val;
    while (pop(&val)) {
        printf("Popped: %d\n", val);
    }
    return 0;
}
