#define _GNU_SOURCE
#include <sys/signalfd.h>
#include <signal.h>
#include <unistd.h>
#include <stdio.h>

int main(void) {
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGINT);

    if (pthread_sigmask(SIG_BLOCK, &mask, NULL) != 0)  /* повертає errno числом */
        return 1;

    int sfd = signalfd(-1, &mask, SFD_CLOEXEC);
    if (sfd < 0) { perror("signalfd"); return 1; }

    struct signalfd_siginfo si;
    if (read(sfd, &si, sizeof si) != (ssize_t) sizeof si) { perror("read"); return 1; }

    printf("signo=%u code=%d pid=%u uid=%u\n",
           si.ssi_signo, si.ssi_code, si.ssi_pid, si.ssi_uid);
    close(sfd);
    return 0;
}
