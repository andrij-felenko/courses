#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <sched.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

int set_batch_policy(void) {
    struct sched_param param;
    memset(&param, 0, sizeof(param));
    param.sched_priority = 0; /* Обов'язково 0 для SCHED_BATCH */

    if (sched_setscheduler(0, SCHED_BATCH, &param) == -1) {
        perror("Помилка sched_setscheduler(SCHED_BATCH)");
        return -1;
    }
    return 0;
}

int set_idle_policy(void) {
    struct sched_param param;
    memset(&param, 0, sizeof(param));
    param.sched_priority = 0; /* Обов'язково 0 для SCHED_IDLE */

    if (sched_setscheduler(0, SCHED_IDLE, &param) == -1) {
        perror("Помилка sched_setscheduler(SCHED_IDLE)");
        return -1;
    }
    return 0;
}

int main(void) {
    printf("Поточний PID: %d. Встановлення SCHED_BATCH...\n", getpid());
    if (set_batch_policy() == 0) {
        printf("Успішно переведено в SCHED_BATCH.\n");
    }

    /* Інтенсивні пакетні обчислення */
    volatile double val = 1.0;
    for (long i = 0; i < 500000000L; ++i) {
        val += i * 0.0000001;
    }

    printf("Зміна політики на SCHED_IDLE...\n");
    if (set_idle_policy() == 0) {
        printf("Успішно переведено в SCHED_IDLE.\n");
    }

    return 0;
}
