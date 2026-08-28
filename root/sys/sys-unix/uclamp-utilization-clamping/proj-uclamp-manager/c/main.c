#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/syscall.h>
#include <linux/sched/types.h>

#ifndef SYS_sched_setattr
#define SYS_sched_setattr 314
#endif

#ifndef SCHED_FLAG_UTIL_CLAMP_MIN
#define SCHED_FLAG_UTIL_CLAMP_MIN 0x20
#endif

#ifndef SCHED_FLAG_UTIL_CLAMP_MAX
#define SCHED_FLAG_UTIL_CLAMP_MAX 0x40
#endif

static int sys_sched_setattr(pid_t pid, const struct sched_attr *attr, unsigned int flags) {
    return syscall(SYS_sched_setattr, pid, attr, flags);
}

int set_thread_uclamp(pid_t tid, unsigned int min_util, unsigned int max_util) {
    struct sched_attr attr;
    memset(&attr, 0, sizeof(attr));
    attr.size = sizeof(attr);
    attr.sched_policy = SCHED_OTHER;

    attr.sched_flags = 0;
    if (min_util <= 1024) {
        attr.sched_flags |= SCHED_FLAG_UTIL_CLAMP_MIN;
        attr.sched_util_min = min_util;
    }
    if (max_util <= 1024) {
        attr.sched_flags |= SCHED_FLAG_UTIL_CLAMP_MAX;
        attr.sched_util_max = max_util;
    }

    if (sys_sched_setattr(tid, &attr, 0) < 0) {
        perror("sys_sched_setattr failed");
        return -1;
    }

    return 0;
}

int main(void) {
    pid_t tid = gettid();
    printf("[C] Налаштування uclamp для потоку TID=%d...\n", tid);

    if (set_thread_uclamp(tid, 600, 1024) == 0) {
        printf("[C] Успішно застосовано профіль Latency-Critical (uclamp_min=600)\n");
    }

    usleep(100000);

    if (set_thread_uclamp(tid, 0, 256) == 0) {
        printf("[C] Успішно застосовано профіль Background Saver (uclamp_max=256)\n");
    }

    return 0;
}
