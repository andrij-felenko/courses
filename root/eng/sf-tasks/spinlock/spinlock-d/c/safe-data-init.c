#include <pthread.h>
#include <stdio.h>
#include <stdbool.h>

typedef struct {
    pthread_spinlock_t lock;
    long shared_counter;
} safe_data_t;

void safe_data_init(safe_data_t *data) {
    data->shared_counter = 0;
    // Ініціалізація POSIX спін-замка для використання в межах одного процесу
    pthread_spin_init(&data->lock, PTHREAD_PROCESS_PRIVATE);
}

void safe_data_increment(safe_data_t *data) {
    // 1. Захоплення спін-замка. Потік активного очікує, не засинаючи.
    pthread_spin_lock(&data->lock);

    // 2. СУВОРИЙ КОНТРАКТ: Всередині критичної секції виконуються лише 
    // надшвидкі неблокуючі операції в оперативній пам'яті.
    // НІЯКИХ printf(), malloc(), read() чи sleep()!
    data->shared_counter++;

    // 3. Негайне звільнення замка після завершення операції
    pthread_spin_unlock(&data->lock);
}

void safe_data_destroy(safe_data_t *data) {
    pthread_spin_destroy(&data->lock);
}
