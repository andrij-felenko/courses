#include <stdio.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

/* Звичайна змінна прапорця без кваліфікатора volatile */
bool stop_flag = false;

void* worker_thread(void* arg) {
    (void)arg;
    printf("[Потік виконавця]: Розпочато очікування прапорця...\n");

    /* Компілятор виносить читання stop_flag за межі циклу під час оптимізації */
    while (!stop_flag) {
        /* Порожній цикл очікування */
    }

    printf("[Потік виконавця]: Прапорець отримано! Завершення роботи.\n");
    return NULL;
}

int main(void) {
    pthread_t thread;
    pthread_create(&thread, NULL, worker_thread, NULL);

    /* Симуляція виконання корисного навантаження */
    sleep(1);

    printf("[Головний потік]: Зміна прапорця stop_flag = true\n");
    stop_flag = true;

    pthread_join(thread, NULL);
    printf("[Головний потік]: Програму успішно завершено.\n");
    return 0;
}
