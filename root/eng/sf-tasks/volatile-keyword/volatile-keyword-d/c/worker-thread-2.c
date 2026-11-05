#include <stdio.h>
#include <stdbool.h>
#include <pthread.h>
#include <unistd.h>

/* Кваліфікатор volatile гарантує пряме звернення до пам'яті при кожному читанні */
volatile bool stop_flag = false;

void* worker_thread(void* arg) {
    (void)arg;
    printf("[Потік виконавця]: Розпочато очікування volatile-прапорця...\n");

    /* Компілятор примусово читає stop_flag з пам'яті на кожній ітерації */
    while (!stop_flag) {
        /* Очікування оновлення значення в оперативній пам'яті */
    }

    printf("[Потік виконавця]: Прапорець помічено у RAM! Завершення роботи.\n");
    return NULL;
}

int main(void) {
    pthread_t thread;
    pthread_create(&thread, NULL, worker_thread, NULL);

    sleep(1);

    printf("[Головний потік]: Запис у volatile-змінну stop_flag = true\n");
    stop_flag = true;

    pthread_join(thread, NULL);
    printf("[Головний потік]: Потік успішно завершив виконання.\n");
    return 0;
}
