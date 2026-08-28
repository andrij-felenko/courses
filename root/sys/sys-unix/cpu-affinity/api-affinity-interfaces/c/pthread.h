#define _GNU_SOURCE
#include <pthread.h>

int pthread_setaffinity_np(pthread_t thread, size_t cpusetsize,
                           const cpu_set_t *cpuset);
int pthread_getaffinity_np(pthread_t thread, size_t cpusetsize,
                           cpu_set_t *cpuset);

int pthread_attr_setaffinity_np(pthread_attr_t *attr, size_t cpusetsize,
                                const cpu_set_t *cpuset);
int pthread_attr_getaffinity_np(pthread_attr_t *attr, size_t cpusetsize,
                                cpu_set_t *cpuset);
