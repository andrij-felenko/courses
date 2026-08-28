/* main.c — Реалізація мовою C */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/sdt.h>

void process_task(int task_id, int worker_id) {
    /* Маркер початку завдання: передаємо task_id та worker_id */
    STAP_PROBE2(workpool, task_start, task_id, worker_id);

    /* Імітація роботи з випадковою затримкою від 10 до 100 мікросекунд */
    struct timespec ts;
    ts.tv_sec = 0;
    ts.tv_nsec = (10 + rand() % 90) * 1000;
    nanosleep(&ts, NULL);

    int status = (rand() % 100 == 0) ? -1 : 0; /* 1% помилок */

    /* Маркер завершення завдання: передаємо task_id, worker_id та status */
    STAP_PROBE3(workpool, task_finish, task_id, worker_id, status);
}

int main(void) {
    srand((unsigned int)time(NULL));
    printf("Сервіс обробки завдань запущену [PID: %d]. Натисніть Ctrl+C для зупинки...\n", getpid());

    int task_counter = 0;
    while (1) {
        int worker_id = rand() % 4;
        process_task(++task_counter, worker_id);
        usleep(5000); /* Пауза 5 мс між завданнями */
    }

    return 0;
}
