#include <stdint.h>
#include <stdbool.h>
#include <stdlib.h>
#include <stdatomic.h>

// Розмір фізичної кєш-лінії більшості сучасних процесорів (64 байти)
#define CACHE_LINE_SIZE 64
#define INITIAL_CELLS_CAPACITY 2

// Структура комірки з вирівнюванням пам'яті проти хибного спільного використання кєшу
typedef struct {
    alignas(CACHE_LINE_SIZE) _Atomic int64_t value;
} long_adder_cell_t;

// Основна структура розщепленого лічильника LongAdder
typedef struct {
    alignas(CACHE_LINE_SIZE) _Atomic int64_t base;
    alignas(CACHE_LINE_SIZE) _Atomic uint32_t cells_busy;
    _Atomic(long_adder_cell_t*) cells;
    _Atomic size_t cells_capacity;
} long_adder_t;

// Ініціалізація об'єкта LongAdder
void long_adder_init(long_adder_t *adder) {
    atomic_init(&adder->base, 0);
    atomic_init(&adder->cells_busy, 0);
    atomic_init(&adder->cells, NULL);
    atomic_init(&adder->cells_capacity, 0);
}

// Додавання значення до лічильника з використанням шардингу та гасіння колізій
void long_adder_add(long_adder_t *adder, int64_t x, uint32_t thread_probe) {
    long_adder_cell_t *cells = atomic_load_explicit(&adder->cells, memory_order_relaxed);
    int64_t b;

    // Швидкий шлях: якщо масив комірок порожній, намагаємося оновити base
    if (cells == NULL) {
        b = atomic_load_explicit(&adder->base, memory_order_relaxed);
        if (atomic_compare_exchange_weak_explicit(&adder->base, &b, b + x,
                                                 memory_order_relaxed,
                                                 memory_order_relaxed)) {
            return; // Оновлення base пройшло успішно без колізії
        }
    }

    // Шардинг: вибір комірки за хешем потоку
    size_t cap = atomic_load_explicit(&adder->cells_capacity, memory_order_relaxed);
    if (cells != NULL && cap > 0) {
        size_t idx = thread_probe & (cap - 1);
        long_adder_cell_t *cell = &cells[idx];
        if (cell != NULL) {
            int64_t v = atomic_load_explicit(&cell->value, memory_order_relaxed);
            if (atomic_compare_exchange_weak_explicit(&cell->value, &v, v + x,
                                                     memory_order_relaxed,
                                                     memory_order_relaxed)) {
                return; // Локальний інкремент у вирівняну комірку успішний
            }
        }
    }

    // Повільний шлях (резервне накопичення при колізіях): оновлюємо base через CAS
    b = atomic_load_explicit(&adder->base, memory_order_relaxed);
    while (!atomic_compare_exchange_weak_explicit(&adder->base, &b, b + x,
                                                  memory_order_release,
                                                  memory_order_relaxed)) {
        // Повторна спроба при колізіях
    }
}

// Обчислення підсумкового значення лічильника (агрегація слабкої узгодженості)
int64_t long_adder_sum(const long_adder_t *adder) {
    int64_t sum = atomic_load_explicit(&adder->base, memory_order_consume);
    long_adder_cell_t *cells = atomic_load_explicit(&adder->cells, memory_order_consume);
    size_t cap = atomic_load_explicit(&adder->cells_capacity, memory_order_relaxed);

    if (cells != NULL) {
        for (size_t i = 0; i < cap; ++i) {
            sum += atomic_load_explicit(&cells[i].value, memory_order_relaxed);
        }
    }
    return sum;
}
