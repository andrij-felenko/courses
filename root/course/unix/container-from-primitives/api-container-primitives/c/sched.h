#define _GNU_SOURCE
#include <sched.h>

int clone(int (*fn)(void *), void *stack, int flags, void *arg, ...
          /* pid_t *parent_tid, void *tls, pid_t *child_tid */);

#include <linux/sched.h>
#include <sys/syscall.h>

long syscall(SYS_clone3, struct clone_args *cl_args, size_t size);
