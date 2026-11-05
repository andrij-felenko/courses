#include <pthread.h>
#include <stdlib.h>

typedef struct {
    pthread_mutex_t lock;
    int shared_value;
} SharedResource;

// Погано: широка критична секція з ручним утриманням блокування під час I/O
void process_bad(SharedResource *res, int input_val) {
    pthread_mutex_lock(&res->lock);
    // Довга обробка та виділення пам'яті під замком — джерело високої конкуренції
    int computed = input_val * 42 + 7;
    res->shared_value += computed;
    pthread_mutex_unlock(&res->lock);
}

// Оптимально: звужена критична секція з підготовкою даних поза замком
void process_good(SharedResource *res, int input_val) {
    // 1. Обчислення виконуються локально у стеку потоку
    int computed = input_val * 42 + 7;

    // 2. Вхід у критичну секцію лише на час модифікації спільного стану
    pthread_mutex_lock(&res->lock);
    res->shared_value += computed;
    pthread_mutex_unlock(&res->lock);
}
