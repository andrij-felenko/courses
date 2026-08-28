/* ipcbench.c — ціна оберту через канал, сокет і спільну пам'ять.
   Збірка: cc -O2 -std=gnu11 -o ipcbench ipcbench.c
   Запуск: ./ipcbench <pipe|seqpacket|shm|spin> <байтів> <обертів> <ядро A> <ядро B> */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <linux/futex.h>
#include <sched.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

#define CLINE 64u

#if defined(__x86_64__) || defined(__i386__)
#define RELAX() __builtin_ia32_pause()
#elif defined(__aarch64__)
#define RELAX() __asm__ __volatile__("yield" ::: "memory")
#else
#define RELAX() ((void)0)
#endif

static uint64_t now_ns(void)
{
        struct timespec t;
        clock_gettime(CLOCK_MONOTONIC, &t);
        return (uint64_t)t.tv_sec * 1000000000ull + (uint64_t)t.tv_nsec;
}

static void pin(int cpu)
{
        cpu_set_t set;
        CPU_ZERO(&set);
        CPU_SET(cpu, &set);
        if (sched_setaffinity(0, sizeof set, &set) != 0)
                perror("sched_setaffinity");
}
