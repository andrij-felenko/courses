#include <stdatomic.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int data_payload[100];
    int status_code;
} payload_t;

typedef struct {
    _Atomic(payload_t*) published_data;
} publisher_t;

void publisher_init(publisher_t* pub) {
    atomic_init(&pub->published_data, NULL);
}

// Оновлення публікації через CAS із коректним впорядкуванням пам'яті
bool publisher_update(publisher_t* pub, payload_t* new_payload) {
    payload_t* expected = atomic_load_explicit(&pub->published_data, memory_order_relaxed);
    
    do {
        // Усі записи у новий new_payload мають бути завершені до публікації
    } while (!atomic_compare_exchange_weak_explicit(
        &pub->published_data,
        &expected,
        new_payload,
        memory_order_release, // Гарантує видимість даних new_payload для читачів
        memory_order_relaxed  // При невдачі використовуємо розслаблений режим
    ));
    
    return true;
}

payload_t* publisher_read(publisher_t* pub) {
    // Acquire гарантує, що зчитування полів payload_t відбудеться після зчитування вказівника
    return atomic_load_explicit(&pub->published_data, memory_order_acquire);
}
