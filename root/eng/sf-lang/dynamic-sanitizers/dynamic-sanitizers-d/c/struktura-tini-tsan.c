#include <pthread.h>
#include <stdio.h>

static int g_shared_counter = 0; // Несинхронізована змінна

void *worker_thread(void *arg) {
    (void)arg;
    for (int i = 0; i < 1000; ++i) {
        g_shared_counter++; // Гонка даних (читання-модифікація-запис)
    }
    return NULL;
}

int main(void) {
    pthread_t t1, t2;
    pthread_create(&t1, NULL, worker_thread, NULL);
    pthread_create(&t2, NULL, worker_thread, NULL);

    pthread_join(t1, NULL);
    pthread_join(t2, NULL);
    return 0;
}
