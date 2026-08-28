#include <signal.h>

int kill(pid_t pid, int sig);                  /* процес або група процесів  */
int killpg(int pgrp, int sig);                 /* тотожне kill(-pgrp, sig)   */
int raise(int sig);                            /* собі                       */
int sigqueue(pid_t pid, int sig, const union sigval value);  /* зі значенням */
int tgkill(pid_t tgid, pid_t tid, int sig);    /* обгортка з glibc 2.30      */

#include <pthread.h>
int pthread_kill(pthread_t thread, int sig);   /* потоку свого процесу       */

/* Обгорток у glibc немає — лише через syscall(2): */
int syscall(SYS_tkill, pid_t tid, int sig);
int syscall(SYS_pidfd_send_signal, int pidfd, int sig,
            siginfo_t *info, unsigned int flags);

union sigval {              /* вантаж, який несе sigqueue() */
    int   sival_int;
    void *sival_ptr;
};
