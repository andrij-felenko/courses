#include <stdatomic.h>
#include <stdbool.h>

// Включення системного заголовка для апаратної паузи на x86
#if defined(__x86_64__) || defined(_M_X64) || defined(__i386__)
#include <emmintrin.h>
#define cpu_relax() _mm_pause()
#else
#define cpu_relax() ((void)0)
#endif

typedef struct {
    atomic_bool flag;
} spinlock_ttas_t;

void spinlock_ttas_init(spinlock_ttas_t *lock) {
    atomic_init(&lock->flag, false);
}

void spinlock_ttas_lock(spinlock_ttas_t *lock) {
    while (true) {
        // 1. Спочатку робимо звичайне неатомарне читання прапорця.
        // Завантажує кеш-лінію у стан Shared (S) і не викликає інвалідацій.
        if (!atomic_load_explicit(&lock->flag, memory_order_relaxed)) {
            // 2. Якщо замок виглядає вільним, робимо атомарну спробу захоплення
            if (!atomic_exchange_explicit(&lock->flag, true, memory_order_acquire)) {
                return; // Успішно захоплено!
            }
        }
        // 3. Апаратна пауза конвеєра процесора для зниження навантаження
        cpu_relax();
    }
}

void spinlock_ttas_unlock(spinlock_ttas_t *lock) {
    atomic_store_explicit(&lock->flag, false, memory_order_release);
}
