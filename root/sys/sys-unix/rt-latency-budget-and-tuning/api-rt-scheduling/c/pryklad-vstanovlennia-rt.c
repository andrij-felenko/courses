#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <string.h>

int configure_thread_rt_and_affinity(pthread_t thread, int priority, int cpu_id) {
    struct sched_param param;
    cpu_set_t cpuset;

    /* 1. Встановлення RT-пріоритету SCHED_FIFO.
       Функції pthread_* повертають код помилки й НЕ встановлюють errno,
       тому тут strerror(ret), а не perror(). */
    param.sched_priority = priority;
    int ret = pthread_setschedparam(thread, SCHED_FIFO, &param);
    if (ret != 0) {
        fprintf(stderr, "pthread_setschedparam failed: %s\n", strerror(ret));
        return ret;
    }

    /* 2. Прив'язка до конкретного ядра CPU */
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    ret = pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
    if (ret != 0) {
        fprintf(stderr, "pthread_setaffinity_np failed: %s\n", strerror(ret));
        return ret;
    }

    return 0;
}
