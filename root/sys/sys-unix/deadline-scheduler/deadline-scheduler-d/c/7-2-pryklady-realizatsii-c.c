#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/sched.h>
#include <stdint.h>
#include <string.h>
#include <sched.h>
#include <errno.h>

struct sched_attr_local {
    uint32_t size;
    uint32_t sched_policy;
    uint64_t sched_flags;
    int32_t  sched_nice;
    uint32_t sched_priority;
    uint64_t sched_runtime;
    uint64_t sched_deadline;
    uint64_t sched_period;
};

static int sys_sched_setattr(pid_t pid, const struct sched_attr_local *attr, unsigned int flags) {
    return syscall(__NR_sched_setattr, pid, attr, flags);
}

int main(void) {
    struct sched_attr_local attr;
    memset(&attr, 0, sizeof(attr));
    
    attr.size = sizeof(attr);
    attr.sched_policy = SCHED_DEADLINE;
    attr.sched_flags = SCHED_FLAG_RECLAIM;

    /* 10 мс runtime, 30 мс deadline та period */
    attr.sched_runtime  = 10 * 1000 * 1000ULL;
    attr.sched_deadline = 30 * 1000 * 1000ULL;
    attr.sched_period   = 30 * 1000 * 1000ULL;

    if (sys_sched_setattr(0, &attr, 0) < 0) {
        perror("Помилка sched_setattr");
        return EXIT_FAILURE;
    }

    for (int i = 0; i < 5; ++i) {
        /* Корисне обчислення реального часу */
        
        /* sched_yield() добровільно віддає залишок бюджету до наступного періоду */
        sched_yield();
    }

    return EXIT_SUCCESS;
}
