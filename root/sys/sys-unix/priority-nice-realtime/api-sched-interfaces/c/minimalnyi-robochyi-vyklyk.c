#define _GNU_SOURCE
#include <errno.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

#ifndef SCHED_DEADLINE
#define SCHED_DEADLINE 6
#endif
#ifndef SCHED_FLAG_DL_OVERRUN
#define SCHED_FLAG_DL_OVERRUN 0x04
#endif

struct sched_attr {
    uint32_t size, sched_policy;
    uint64_t sched_flags;
    int32_t  sched_nice;
    uint32_t sched_priority;
    uint64_t sched_runtime, sched_deadline, sched_period;
};

static void do_one_job(void)              /* робота, що вкладається в бюджет */
{
    struct timespec t0, t;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    do {
        clock_gettime(CLOCK_MONOTONIC, &t);
    } while ((t.tv_sec - t0.tv_sec) * 1000000000LL
             + (t.tv_nsec - t0.tv_nsec) < 800000LL);      /* 800 мкс */
}

int main(void)
{
    struct sched_attr a;
    memset(&a, 0, sizeof a);              /* сміття в полях = EINVAL */
    a.size           = sizeof a;
    a.sched_policy   = SCHED_DEADLINE;
    a.sched_flags    = SCHED_FLAG_DL_OVERRUN;   /* SIGXCPU, якщо не вклалися */
    a.sched_runtime  = 1200 * 1000;             /* 1.2 мс */
    a.sched_deadline = 2500 * 1000;             /* 2.5 мс */
    a.sched_period   = 5000 * 1000;             /* 5.0 мс */

    if (syscall(SYS_sched_setattr, 0, &a, 0u) != 0) {
        switch (errno) {
        case EPERM:  fprintf(stderr, "немає CAP_SYS_NICE або звужена маска ядер\n"); break;
        case EBUSY:  fprintf(stderr, "смуга вичерпана: сума часток не влазить\n");   break;
        case EINVAL: fprintf(stderr, "порушено runtime ≤ deadline ≤ period\n");      break;
        default:     perror("sched_setattr");
        }
        return 1;
    }

    for (int i = 0; i < 10; i++) {
        do_one_job();
        sched_yield();          /* «на цей період усе» — чекаємо наступного */
    }
    return 0;
}
