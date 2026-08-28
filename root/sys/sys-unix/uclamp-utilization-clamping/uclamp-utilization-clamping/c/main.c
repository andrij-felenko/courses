#define _GNU_SOURCE
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <sys/syscall.h>
#include <linux/sched/types.h>

#ifndef SYS_sched_setattr
#define SYS_sched_setattr 314
#endif

#ifndef SCHED_FLAG_UTIL_CLAMP
#define SCHED_FLAG_UTIL_CLAMP 0x60
#endif

int main(void) {
    struct sched_attr attr;
    memset(&attr, 0, sizeof(attr));
    attr.size = sizeof(attr);
    attr.sched_policy = SCHED_OTHER;

    /* Встановлюємо uclamp_min = 512 (50%) та uclamp_max = 768 (75%) */
    attr.sched_flags = SCHED_FLAG_UTIL_CLAMP;
    attr.sched_util_min = 512;
    attr.sched_util_max = 768;

    if (syscall(SYS_sched_setattr, 0, &attr, 0) == 0) {
        printf("uclamp успішно застосовано!\n");
    }
    return 0;
}
