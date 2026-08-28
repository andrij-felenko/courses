#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <stdbool.h>

bool setup_realtime_thread(int core_id, int priority) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) != 0) {
        return false;
    }

    struct sched_param param;
    param.sched_priority = priority;
    return (pthread_setschedparam(pthread_self(), SCHED_FIFO, &param) == 0);
}
