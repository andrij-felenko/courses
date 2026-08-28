#include <sys/syscall.h>
#include <unistd.h>
#include <signal.h>
#include <stdio.h>

/* Надіслати SIGTERM саме тому процесові, якого ми мали на увазі.
   pidfd_open — Linux 5.3, pidfd_send_signal — Linux 5.1;
   обгорток у glibc немає ні для того, ні для того. */
int term_exactly(pid_t pid)
{
    int pidfd = syscall(SYS_pidfd_open, pid, 0);
    if (pidfd < 0) {
        perror("pidfd_open");            /* процес уже помер — і це видно тут */
        return -1;
    }

    /* info == NULL → поводиться як kill(): одержувач побачить SI_USER.
       flags == 0 → обсяг береться з самого pidfd (процес, не потік).      */
    int rc = syscall(SYS_pidfd_send_signal, pidfd, SIGTERM, NULL, 0);
    if (rc < 0)
        perror("pidfd_send_signal");     /* ESRCH тут означає саме смерть   */

    close(pidfd);
    return rc;
}
