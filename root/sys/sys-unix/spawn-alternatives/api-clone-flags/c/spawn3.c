/* spawn3.c — clone3 з відступом на clone, коли ядро надто старе.
 *   gcc -O2 -Wall -o spawn3 spawn3.c && ./spawn3
 * Підключаємо саме <linux/sched.h>: прапорці визначені і в ньому,
 * і в glibc-івському <sched.h>, тож обидва разом брати не варто.
 * P_PIDFD у waitid — це ядро 5.4, а в glibc константа з'явилася аж у 2.36.
 */
#define _GNU_SOURCE
#include <errno.h>
#include <linux/sched.h>
#include <linux/types.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>

static long spawn_task(int *pidfd_out)
{
    struct clone_args args = {
        .flags       = CLONE_PIDFD | CLONE_CLEAR_SIGHAND,
        .pidfd       = (__u64)(uintptr_t)pidfd_out,
        .exit_signal = SIGCHLD,
    };
    long pid = syscall(SYS_clone3, &args, sizeof args);
    if (pid >= 0 || (errno != ENOSYS && errno != EINVAL && errno != E2BIG))
        return pid;                 /* або вийшло, або зламалося по суті */

    /* ENOSYS — ядро старіше за 5.3; EINVAL — воно не знає CLONE_CLEAR_SIGHAND;
       E2BIG — заголовок новіший за ядро. Відступаємо на старий виклик:
       CLONE_PIDFD там є з 5.2, але дескриптор віддається через parent_tid. */
    return syscall(SYS_clone, (unsigned long)(CLONE_PIDFD | SIGCHLD),
                   NULL, pidfd_out, NULL, 0UL);      /* порядок для x86-64 */
}

int main(void)
{
    int pidfd = -1;
    long pid = spawn_task(&pidfd);
    if (pid < 0) { perror("clone"); return 1; }

    if (pid == 0) {                 /* сирий виклик повертається двічі */
        execlp("id", "id", (char *)NULL);
        _exit(127);
    }

    siginfo_t info;
    if (waitid(P_PIDFD, (id_t)pidfd, &info, WEXITED) == 0)
        printf("дитина %d вийшла з кодом %d\n", info.si_pid, info.si_status);
    close(pidfd);
    return 0;
}
