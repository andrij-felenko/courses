// chaos_inject.c
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <dlfcn.h>
#include <sched.h>
#include <unistd.h>

static int (*real_pthread_mutex_lock)(void *) = NULL;

int pthread_mutex_lock(void *mutex) {
    if (!real_pthread_mutex_lock) {
        real_pthread_mutex_lock = (int (*)(void *))dlsym(RTLD_NEXT, "pthread_mutex_lock");
    }

    // Випадкова поступка кванта часу процесора перед взяттям блокування
    if (rand() % 4 == 0) {
        sched_yield();
    }
    if (rand() % 10 == 0) {
        usleep(rand() % 50); // Пауза від 0 до 50 мікросекунд
    }

    return real_pthread_mutex_lock(mutex);
}
