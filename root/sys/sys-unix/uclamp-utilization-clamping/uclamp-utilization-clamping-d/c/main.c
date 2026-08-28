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

static int set_uclamp(pid_t tid, unsigned int min_val, unsigned int max_val) {
    struct sched_attr attr;
    memset(&attr, 0, sizeof(attr));
    attr.size = sizeof(attr);
    attr.sched_policy = SCHED_OTHER;

    attr.sched_flags = SCHED_FLAG_UTIL_CLAMP_MIN | SCHED_FLAG_UTIL_CLAMP_MAX;
    attr.sched_util_min = min_val; /* Шкала 0 .. 1024 */
    attr.sched_util_max = max_val;

    if (syscall(SYS_sched_setattr, tid, &attr, 0) < 0) {
        perror("sched_setattr failed");
        return -1;
    }
    return 0;
}

int main(void) {
    pid_t tid = gettid();
    
    if (set_uclamp(tid, 512, 768) == 0) {
        printf("uclamp успішно застосовано для TID %d: min=512, max=768\n", tid);
    }
    
    return 0;
}
