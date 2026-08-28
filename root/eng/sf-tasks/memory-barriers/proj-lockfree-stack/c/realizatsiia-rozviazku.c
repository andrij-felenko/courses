// Тегований CAS мовою C (128-бітний atomic на x86_64)
#include <stdatomic.h>
#include <stdint.h>

struct tagged_ptr {
    struct node *ptr;
    uintptr_t tag;
};

// Використання cmpxchg16b на x86_64 для атомарного порівняння вказівника й лічильника
typedef _Atomic(struct tagged_ptr) atomic_tagged_ptr;

void push_tagged(atomic_tagged_ptr *top, struct node *n)
{
    struct tagged_ptr old_top = atomic_load_explicit(top, memory_order_relaxed);
    struct tagged_ptr new_top;

    do {
        n->next = old_top.ptr;
        new_top.ptr = n;
        new_top.tag = old_top.tag + 1; // Інкрементуємо тег версії!
    } while (!atomic_compare_exchange_weak_explicit(
                top, &old_top, new_top,
                memory_order_release, memory_order_relaxed));
}
