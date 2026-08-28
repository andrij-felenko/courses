/* 1. Обгортка glibc — це не системний виклик, а функція поверх нього */
#define _GNU_SOURCE
#include <sched.h>
int clone(int (*fn)(void *), void *stack, int flags, void *arg,
          ... /* pid_t *parent_tid, void *tls, pid_t *child_tid */ );

/* 2. Сирий clone — порядок аргументів залежить від архітектури (нижче x86-64) */
#include <sys/syscall.h>
long syscall(SYS_clone, unsigned long flags, void *stack,
             int *parent_tid, int *child_tid, unsigned long tls);

/* 3. clone3 — обгортки в glibc немає взагалі, лише сирий виклик */
long syscall(SYS_clone3, struct clone_args *cl_args, size_t size);
