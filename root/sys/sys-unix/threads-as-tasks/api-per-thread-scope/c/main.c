#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <sys/resource.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <limits.h>

static void report(const char *tag)
{
    char cwd[PATH_MAX];
    cpu_set_t set;

    CPU_ZERO(&set);
    sched_getaffinity(0, sizeof set, &set);   /* 0 = ця задача */
    printf("%-11s tid=%-6ld nice=%-3d ядер=%-2d cwd=%s\n",
           tag, (long)syscall(SYS_gettid),
           getpriority(PRIO_PROCESS, 0), CPU_COUNT(&set),
           getcwd(cwd, sizeof cwd));
}

static void *worker(void *arg)
{
    cpu_set_t one;

    (void)arg;
    report("потік");
    setpriority(PRIO_PROCESS, 0, 5);          /* своє */
    CPU_ZERO(&one); CPU_SET(0, &one);
    sched_setaffinity(0, sizeof one, &one);   /* своє */
    chdir("/tmp");                            /* спільне! */
    report("потік*");
    return NULL;
}

int main(void)
{
    pthread_t t;

    report("головний");
    pthread_create(&t, NULL, worker, NULL);
    pthread_join(t, NULL);
    report("головний*");
    return 0;
}
