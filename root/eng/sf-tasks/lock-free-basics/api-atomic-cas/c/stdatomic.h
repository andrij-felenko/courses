#include <stdatomic.h>
#include <stdbool.h>

// Сильний варіант: успіх або гарантована невідповідність значення
bool atomic_compare_exchange_strong(
    volatile _Atomic(T)* object,
    T* expected,
    T desired
);

// Слабкий варіант: дозволяє хибні збої для оптимізації циклів
bool atomic_compare_exchange_weak(
    volatile _Atomic(T)* object,
    T* expected,
    T desired
);

// Варіанти з явним зазначенням моделей пам'яті для успіху та невдачі
bool atomic_compare_exchange_strong_explicit(
    volatile _Atomic(T)* object,
    T* expected,
    T desired,
    memory_order success_order,
    memory_order failure_order
);

bool atomic_compare_exchange_weak_explicit(
    volatile _Atomic(T)* object,
    T* expected,
    T desired,
    memory_order success_order,
    memory_order failure_order
);
