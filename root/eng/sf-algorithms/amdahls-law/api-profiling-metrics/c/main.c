#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <stdio.h>

/* Прив'язка потоку thread до логічного ядра core_id через POSIX API */
int pin_thread_to_core(pthread_t thread, int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    int res = pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
    if (res != 0) {
        perror("Помилка встановлення афінності потоку");
        return -1;
    }
    return 0;
}
