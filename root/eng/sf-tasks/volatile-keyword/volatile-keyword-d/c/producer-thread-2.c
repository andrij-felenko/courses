#include <stdio.h>
#include <stdbool.h>
#include <pthread.h>
#include <stdatomic.h>

/* Атомарні змінні замість volatile забезпечують і атомарність, і бар'єри пам'яті */
atomic_bool data_ready = ATOMIC_VAR_INIT(false);
atomic_int event_counter = ATOMIC_VAR_INIT(0);
int shared_payload = 0;

void* producer_thread(void* arg) {
    (void)arg;
    shared_payload = 42; /* Підготовка даних */

    /* Атомарне збереження з семантикою release виштовхує записи у RAM */
    atomic_store_explicit(&data_ready, true, memory_order_release);

    /* Атомарний інкремент без стану гонитви */
    atomic_fetch_add_explicit(&event_counter, 1, memory_order_relaxed);
    return NULL;
}

void* consumer_thread(void* arg) {
    (void)arg;

    /* Атомарне читання з семантикою acquire гарантує впорядкованість */
    while (!atomic_load_explicit(&data_ready, memory_order_acquire)) {
        /* Пасивне очікування */
    }

    printf("[Споживач C11]: Прочитано payload = %d, всього подій = %d\n",
           shared_payload, atomic_load(&event_counter));
    return NULL;
}

int main(void) {
    pthread_t p, c;
    pthread_create(&p, NULL, producer_thread, NULL);
    pthread_create(&c, NULL, consumer_thread, NULL);

    pthread_join(p, NULL);
    pthread_join(c, NULL);
    return 0;
}
