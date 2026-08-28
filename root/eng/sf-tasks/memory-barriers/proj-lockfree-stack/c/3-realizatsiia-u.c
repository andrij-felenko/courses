// Ідіоматична реалізація мовою C11 (stdatomic.h)
#include <stdatomic.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>

struct node {
    int data;
    struct node *next;
};

struct lockfree_stack {
    _Atomic(struct node *) top;
};

void stack_init(struct lockfree_stack *s)
{
    atomic_store_explicit(&s->top, NULL, memory_order_relaxed);
}

void stack_push(struct lockfree_stack *s, int val)
{
    struct node *new_node = malloc(sizeof(*new_node));
    if (!new_node) return;

    new_node->data = val;

    struct node *old_top = atomic_load_explicit(&s->top, memory_order_relaxed);
    do {
        new_node->next = old_top;
        // Запис у разі успіху використовує Release, читання у разі невдачі — Relaxed
    } while (!atomic_compare_exchange_weak_explicit(
                &s->top, &old_top, new_node,
                memory_order_release, memory_order_relaxed));
}

bool stack_pop(struct lockfree_stack *s, int *val)
{
    struct node *old_top = atomic_load_explicit(&s->top, memory_order_acquire);
    struct node *new_top;

    do {
        if (!old_top)
            return false;

        new_top = old_top->next;
    } while (!atomic_compare_exchange_weak_explicit(
                &s->top, &old_top, new_top,
                memory_order_acquire, memory_order_acquire));

    *val = old_top->data;
    free(old_top); // У користувацькому просторі для продакшену потрібні Hazard Pointers!
    return true;
}
