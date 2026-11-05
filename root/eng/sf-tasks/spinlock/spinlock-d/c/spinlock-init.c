#include <stdatomic.h>
#include <stdbool.h>

// Структура спін-замка на основі стандартного атомарного прапорця
typedef struct {
    atomic_flag flag;
} spinlock_t;

// Ініціалізація спін-замка у вільному стані
void spinlock_init(spinlock_t *lock) {
    // Метод atomic_flag_clear атомарно встановлює прапорець у стан false
    atomic_flag_clear(&lock->flag);
}

// Захоплення спін-замка за допомогою атомарного активного очікування
void spinlock_lock(spinlock_t *lock) {
    // atomic_flag_test_and_set_explicit атомарно встановлює прапорець у true
    // та повертає значення, яке було до запису.
    // Використовується memory_order_acquire для запобігання перенесенню 
    // читань/записів із критичної секції вище межі захоплення замка.
    while (atomic_flag_test_and_set_explicit(&lock->flag, memory_order_acquire)) {
        // Активне крутіння на процесорному ядрі без виклику операційної системи
    }
}

// Звільнення спін-замка
void spinlock_unlock(spinlock_t *lock) {
    // Використовується memory_order_release для гарантії того, що всі зміни, 
    // зроблені всередині критичної секції, стануть видимими іншим ядрам 
    // до того, як замок буде офіційно звільнено.
    atomic_flag_clear_explicit(&lock->flag, memory_order_release);
}
