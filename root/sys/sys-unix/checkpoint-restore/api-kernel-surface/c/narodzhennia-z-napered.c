#define _GNU_SOURCE
#include <linux/sched.h>
#include <sys/syscall.h>
#include <signal.h>
#include <stdint.h>
#include <unistd.h>

static pid_t spawn_with_pid(pid_t want)
{
    pid_t tids[1] = { want };
    struct clone_args args = {
        .exit_signal  = SIGCHLD,
        .set_tid      = (uint64_t) (uintptr_t) tids,
        .set_tid_size = 1,
    };
    /* обгортки в glibc немає — лише сирий виклик */
    return syscall(__NR_clone3, &args, sizeof args);
}
