#define _GNU_SOURCE
#include <sched.h>
#include <pthread.h>

/* Встановлення маски дозволених ядер для процесу за його PID */
int sched_setaffinity(pid_t pid, size_t cpusetsize, const cpu_set_t *mask);

/* Отримання поточної маски дозволених ядер для процесу */
int sched_getaffinity(pid_t pid, size_t cpusetsize, cpu_set_t *mask);

/* Прив'язка конкретного POSIX-потоку до маски ядер */
int pthread_setaffinity_np(pthread_t thread, size_t cpusetsize, const cpu_set_t *cpuset);

/* Отримання маски ядер для конкретного POSIX-потоку */
int pthread_getaffinity_np(pthread_t thread, size_t cpusetsize, cpu_set_t *cpuset);
