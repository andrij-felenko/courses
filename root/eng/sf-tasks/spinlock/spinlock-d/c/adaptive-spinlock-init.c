#include <stdatomic.h>
#include <stdbool.h>
#include <sched.h>

// Визначення апаратної паузи для архітектури x86
#if defined(__x86_64__) || defined(_M_X64) || defined(__i386__)
#include <emmintrin.h>
#define cpu_relax() _mm_pause()
#else
#define cpu_relax() ((void)0)
#endif

// Максимальна кількість спроб активного очікування до поступання часом
#define ADAPTIVE_SPIN_LIMIT 1000

typedef struct {
    atomic_bool locked;
} adaptive_spinlock_t;

void adaptive_spinlock_init(adaptive_spinlock_t *lock) {
    atomic_init(&lock->locked, false);
}

void adaptive_spinlock_lock(adaptive_spinlock_t *lock) {
    // 1. Фаза активного очікування в просторі користувача з інструкцією PAUSE
    for (int i = 0; i < ADAPTIVE_SPIN_LIMIT; ++i) {
        if (!atomic_load_explicit(&lock->locked, memory_order_relaxed)) {
            if (!atomic_exchange_explicit(&lock->locked, true, memory_order_acquire)) {
                return; // Успішне миттєве захоплення без системного виклику!
            }
        }
        cpu_relax();
    }

    // 2. Фаза поступання процесорним часом планувальнику при тривалій конкуренції
    while (atomic_exchange_explicit(&lock->locked, true, memory_order_acquire)) {
        sched_yield(); // Повертає управління ОС для запобігання марному спалюванню ЦП
    }
}

void adaptive_spinlock_unlock(adaptive_spinlock_t *lock) {
    atomic_store_explicit(&lock->locked, false, memory_order_release);
}
