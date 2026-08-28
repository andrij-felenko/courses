#define _GNU_SOURCE
#include <linux/sched.h>
#include <poll.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void) {
    int pidfd = -1;
    struct clone_args a = {
        .flags       = CLONE_PIDFD,
        .pidfd       = (uint64_t)(uintptr_t)&pidfd,
        .exit_signal = SIGCHLD,
    };

    pid_t child = syscall(SYS_clone3, &a, sizeof a);
    if (child == 0) {                       /* дитина */
        execl("/bin/sleep", "sleep", "30", (char *)NULL);
        _exit(127);
    }

    struct pollfd pf = { .fd = pidfd, .events = POLLIN };
    int ready = poll(&pf, 1, 2000);         /* чекаємо 2 с */

    if (ready == 0) {                       /* не дочекалися — просимо піти */
        syscall(SYS_pidfd_send_signal, pidfd, SIGTERM, NULL, 0);
        poll(&pf, 1, -1);
    }

    siginfo_t info = { 0 };
    waitid(P_PIDFD, (id_t)pidfd, &info, WEXITED);
    printf("pid=%d code=%d status=%d\n", info.si_pid, info.si_code, info.si_status);

    close(pidfd);
    return 0;
}
