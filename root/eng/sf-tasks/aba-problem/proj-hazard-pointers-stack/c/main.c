#include <stdio.h>
#include <stdlib.h>
#include <stdatomic.h>
#include <stdbool.h>

#define MAX_THREADS 8
#define MAX_HAZARD_PER_THREAD 2

typedef struct Node {
    int data;
    struct Node* next;
} Node;

_Atomic(Node*) hazard_pointers[MAX_THREADS * MAX_HAZARD_PER_THREAD];
_Atomic(Node*) stack_head = NULL;

void hp_set(int thread_id, Node* ptr) {
    atomic_store_explicit(&hazard_pointers[thread_id], ptr, memory_order_release);
}

void hp_clear(int thread_id) {
    atomic_store_explicit(&hazard_pointers[thread_id], NULL, memory_order_release);
}

bool hp_is_protected(Node* ptr) {
    for (int i = 0; i < MAX_THREADS * MAX_HAZARD_PER_THREAD; i++) {
        if (atomic_load_explicit(&hazard_pointers[i], memory_order_acquire) == ptr) {
            return true;
        }
    }
    return false;
}

void push(int val) {
    Node* new_node = (Node*)malloc(sizeof(Node));
    new_node->data = val;
    Node* old_head = atomic_load_explicit(&stack_head, memory_order_relaxed);
    do {
        new_node->next = old_head;
    } while (!atomic_compare_exchange_weak_explicit(
        &stack_head, &old_head, new_node, memory_order_release, memory_order_relaxed));
}

bool pop(int thread_id, int* val) {
    Node* head;
    do {
        head = atomic_load_explicit(&stack_head, memory_order_acquire);
        if (!head) return false;
        hp_set(thread_id, head);
        if (atomic_load_explicit(&stack_head, memory_order_acquire) != head) {
            hp_clear(thread_id);
            continue;
        }
        Node* next = head->next;
        if (atomic_compare_exchange_weak_explicit(
            &stack_head, &head, next, memory_order_release, memory_order_relaxed)) {
            *val = head->data;
            hp_clear(thread_id);
            free(head);
            return true;
        }
        hp_clear(thread_id);
    } while (true);
}

int main(void) {
    printf("=== Lock-Free Treiber Stack with Hazard Pointers (C) ===\n");
    push(10);
    push(20);
    push(30);

    int val;
    if (pop(0, &val)) printf("Popped: %d\n", val);
    if (pop(0, &val)) printf("Popped: %d\n", val);
    if (pop(0, &val)) printf("Popped: %d\n", val);

    return 0;
}
