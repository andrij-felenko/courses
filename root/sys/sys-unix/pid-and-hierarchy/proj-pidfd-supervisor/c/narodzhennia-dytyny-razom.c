#define _GNU_SOURCE
#include <linux/sched.h>      /* struct clone_args */
#include <sched.h>            /* CLONE_PIDFD */
#include <sys/syscall.h>

#include <errno.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/epoll.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

static long sys_clone3(struct clone_args *a, size_t sz)
{ return syscall(SYS_clone3, a, sz); }

static int sys_pidfd_open(pid_t pid, unsigned int flags)
{ return (int)syscall(SYS_pidfd_open, pid, flags); }

static int sys_pidfd_kill(int fd, int sig, unsigned int flags)
{ return (int)syscall(SYS_pidfd_send_signal, fd, sig, (siginfo_t *)NULL, flags); }

static long now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}
