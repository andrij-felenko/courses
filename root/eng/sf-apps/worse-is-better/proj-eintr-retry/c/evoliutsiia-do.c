#define _GNU_SOURCE
#include <sys/signalfd.h>
#include <signal.h>
#include <pthread.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

int create_signal_channel(void) {
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGINT);
    sigaddset(&mask, SIGTERM);

    // Блокуємо сигнали для поточного потоку
    if (pthread_sigmask(SIG_BLOCK, &mask, NULL) == -1) {
        perror("pthread_sigmask");
        return -1;
    }

    // Створюємо файловий дескриптор для читання сигналів
    int sfd = signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
    if (sfd == -1) {
        perror("signalfd");
        return -1;
    }
    return sfd;
}
