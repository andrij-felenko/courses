#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/syscall.h>
#include <linux/sched.h>

#ifndef SYS_sched_setattr
#if defined(__x86_64__)
#define SYS_sched_setattr 314
#elif defined(__aarch64__)
#define SYS_sched_setattr 274
#elif defined(__riscv)
#define SYS_sched_setattr 274
#endif
#endif

#ifndef SCHED_FLAG_RESET_ON_FORK
#define SCHED_FLAG_RESET_ON_FORK 0x01
#endif

struct local_sched_attr {
    uint32_t size;
    uint32_t sched_policy;
    uint64_t sched_flags;
    int32_t  sched_nice;
    uint32_t sched_priority;
    uint64_t sched_runtime;
    uint64_t sched_deadline;
    uint64_t sched_period;
};

static int sys_sched_setattr(pid_t pid, const struct local_sched_attr *attr, unsigned int flags) {
    return (int)syscall(SYS_sched_setattr, pid, attr, flags);
}

int set_process_batch_policy(pid_t pid, int nice_val, int reset_on_fork) {
    struct local_sched_attr attr;
    memset(&attr, 0, sizeof(attr));
    
    attr.size = sizeof(attr);
    attr.sched_policy = SCHED_BATCH;
    attr.sched_nice = nice_val;
    attr.sched_priority = 0; // Для SCHED_BATCH пріоритет завжди 0
    
    if (reset_on_fork) {
        attr.sched_flags |= SCHED_FLAG_RESET_ON_FORK;
    }
    
    if (sys_sched_setattr(pid, &attr, 0) < 0) {
        perror("sched_setattr SCHED_BATCH failed");
        return -1;
    }
    return 0;
}
