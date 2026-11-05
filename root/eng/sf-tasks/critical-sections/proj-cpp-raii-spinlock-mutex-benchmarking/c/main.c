#include <stdio.h>
#include <stdatomic.h>
#include <stdbool.h>

typedef struct {
    atomic_flag flag;
} spinlock_t;

#define SPINLOCK_INIT { ATOMIC_FLAG_INIT }

void spinlock_lock(spinlock_t* lock) {
    while (atomic_flag_test_and_set_explicit(&lock->flag, memory_order_acquire)) {
        #if defined(__x86_64__) || defined(_M_X64)
        __builtin_ia32_pause();
        #endif
    }
}

void spinlock_unlock(spinlock_t* lock) {
    atomic_flag_clear_explicit(&lock->flag, memory_order_release);
}

int main(void) {
    printf("=== C Atomic Flag Spinlock Implementation ===\n");
    spinlock_t lock = SPINLOCK_INIT;

    spinlock_lock(&lock);
    printf("Acquired spinlock!\n");
    spinlock_unlock(&lock);
    printf("Released spinlock!\n");

    return 0;
}
