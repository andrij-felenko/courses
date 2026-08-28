#include <sys/prctl.h>
#include <signal.h>
#include <unistd.h>
#include <stdio.h>

int enable_parent_death_signal(int signum) {
    /* Надіслати signum дочірньому процесу, коли його батько завершується */
    if (prctl(PR_SET_PDEATHSIG, signum) < 0) {
        return -1;
    }
    /* Перевіряємо race condition: чи не помер батько до виклику prctl */
    if (getppid() == 1) {
        /* Батько вже загинув до реєстрації сигналу */
        kill(getpid(), signum);
    }
    return 0;
}
