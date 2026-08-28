#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <sched.h>
#include <time.h>
#include <sys/mman.h>
#include <unistd.h>

#define NSEC_PER_SEC 1000000000L
#define PERIOD_NS    1000000L // 1 мілісекунда

static pthread_mutex_t spi_mutex;

void* real_time_thread(void* arg) {
    struct timespec next_period;
    clock_gettime(CLOCK_MONOTONIC, &next_period);

    while (1) {
        // Розрахунок наступної абсолютної часової мітки
        next_period.tv_nsec += PERIOD_NS;
        if (next_period.tv_nsec >= NSEC_PER_SEC) {
            next_period.tv_nsec -= NSEC_PER_SEC;
            next_period.tv_sec += 1;
        }

        // Абсолютне засинання без накопичення джитеру
        clock_nanosleep(CLOCK_MONOTONIC, TIMER_ABSTIME, &next_period, NULL);

        // Критична секція з успадкуванням пріоритету
        if (pthread_mutex_lock(&spi_mutex) == 0) {
            // Виконання операцій керування
            pthread_mutex_unlock(&spi_mutex);
        }
    }
    return NULL;
}

int main(void) {
    // 1. Блокування всіх сторінок процесу в фізичній пам'яті (RAM)
    if (mlockall(MCL_CURRENT | MCL_FUTURE) == -1) {
        perror("mlockall failed");
        exit(EXIT_FAILURE);
    }

    // 2. Налаштування м'ютекса з Priority Inheritance
    pthread_mutexattr_t mutex_attr;
    pthread_mutexattr_init(&mutex_attr);
    pthread_mutexattr_setprotocol(&mutex_attr, PTHREAD_PRIO_INHERIT);
    pthread_mutex_init(&spi_mutex, &mutex_attr);
    pthread_mutexattr_destroy(&mutex_attr);

    // 3. Налаштування атрибутів потоку для політики SCHED_FIFO
    pthread_t thread_id;
    pthread_attr_t attr;
    struct sched_param param;

    pthread_attr_init(&attr);
    pthread_attr_setinheritsched(&attr, PTHREAD_EXPLICIT_SCHED);
    pthread_attr_setschedpolicy(&attr, SCHED_FIFO);
    param.sched_priority = 99; // Найвищий пріоритет реального часу
    pthread_attr_setschedparam(&attr, &param);

    // 4. Запуск потоку реального часу
    if (pthread_create(&thread_id, &attr, real_time_thread, NULL) != 0) {
        perror("pthread_create failed (потрібні права root/CAP_SYS_NICE)");
        exit(EXIT_FAILURE);
    }

    pthread_attr_destroy(&attr);
    pthread_join(thread_id, NULL);
    return 0;
}
