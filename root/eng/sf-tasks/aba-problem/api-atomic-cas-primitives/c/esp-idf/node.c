#include <stdatomic.h>
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

typedef struct node {
    uint32_t data;
    struct node *next;
} node_t;

// Версіонований вказівник для вирішення проблеми ABA на 32-бітній архітектурі
typedef struct {
    node_t *ptr;
    uint32_t tag;
} tagged_ptr_t;

typedef struct {
    _Atomic tagged_ptr_t head;
} lf_stack_t;

void lf_stack_init(lf_stack_t *stack) {
    tagged_ptr_t init_val = { .ptr = NULL, .tag = 0 };
    atomic_init(&stack->head, init_val);
}

// Вилучення елемента зі стеку з експоненційною затримкою та захистом від ABA
bool lf_stack_pop(lf_stack_t *stack, uint32_t *out_data) {
    tagged_ptr_t expected = atomic_load_explicit(&stack->head, memory_order_relaxed);
    tagged_ptr_t desired;
    uint32_t backoff_delay = 1;

    while (expected.ptr != NULL) {
        desired.ptr = expected.ptr->next;
        desired.tag = expected.tag + 1; // Збільшуємо тег для унікальності стану

        if (atomic_compare_exchange_weak_explicit(
                &stack->head,
                &expected,
                desired,
                memory_order_acquire,
                memory_order_relaxed)) {
            *out_data = expected.ptr->data;
            return true;
        }

        // Експоненційне затримання під час високої колізії кеш-ліній
        for (volatile uint32_t i = 0; i < backoff_delay; ++i) {
            __asm__ volatile("nop");
        }
        if (backoff_delay < 64) {
            backoff_delay <<= 1;
        }
    }

    return false;
}
