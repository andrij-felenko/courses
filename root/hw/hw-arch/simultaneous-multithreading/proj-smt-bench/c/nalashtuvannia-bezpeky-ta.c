#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <sys/prctl.h>
#include <unistd.h>
#include <errno.h>

#ifndef PR_SCHED_CORE
#define PR_SCHED_CORE 62
#define PR_SCHED_CORE_CREATE 1
#define PR_SCHED_CORE_SCOPE_THREAD 0
#endif

// Увімкнення Core Scheduling: створення унікального домену довіри
int isolate_thread_group(void) {
    int res = prctl(PR_SCHED_CORE, PR_SCHED_CORE_CREATE, 0, PR_SCHED_CORE_SCOPE_THREAD, 0);
    if (res < 0) {
        perror("prctl(PR_SCHED_CORE)");
        return -1;
    }
    printf("[PID %d] Створено ізольований домен Core Scheduling
", getpid());
    return 0;
}
