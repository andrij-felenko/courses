#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <errno.h>
#include <string.h>
#include <sys/prctl.h>
#include <unistd.h>

#ifndef PR_SCHED_CORE
#define PR_SCHED_CORE 62
#define PR_SCHED_CORE_GET 0
#define PR_SCHED_CORE_CREATE 1
#define PIDTYPE_PID 0
#define PIDTYPE_TGID 1
#endif

int enable_core_scheduling_isolation(void) {
    /* Створюємо новий унікальний домен довіри для всієї групи ниток */
    int res = prctl(PR_SCHED_CORE, PR_SCHED_CORE_CREATE, 0, PIDTYPE_TGID, 0);
    if (res < 0) {
        if (errno == ENODEV) {
            fprintf(stderr, "SMT неактивний або ядра не підтримують SMT\n");
            return 0;
        }
        fprintf(stderr, "Помилка prctl(PR_SCHED_CORE_CREATE): %s\n", strerror(errno));
        return -1;
    }

    uint64_t cookie = 0;
    res = prctl(PR_SCHED_CORE, PR_SCHED_CORE_GET, 0, PIDTYPE_PID, (unsigned long)&cookie);
    if (res == 0) {
        printf("Core Scheduling активовано успішно. Cookie домену довіри: 0x%lx\n", cookie);
    }
    return 0;
}

int main(void) {
    return enable_core_scheduling_isolation();
}
