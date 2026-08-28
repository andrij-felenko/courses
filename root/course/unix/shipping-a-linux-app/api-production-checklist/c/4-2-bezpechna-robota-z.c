#define _GNU_SOURCE
#include <sys/types.h>
#include <sys/socket.h>
#include <signal.h>
#include <unistd.h>
#include <errno.h>
#include <stdio.h>

/* Безпечна відправка даних у мережевий сокет */
ssize_t safe_socket_send(int fd, const void *buf, size_t len) {
    /* Передаємо прапорець MSG_NOSIGNAL, який забороняє генерацію SIGPIPE */
    ssize_t res = send(fd, buf, len, MSG_NOSIGNAL);
    if (res < 0) {
        if (errno == EPIPE || errno == ECONNRESET) {
            /* Клієнт розірвав з'єднання — фіксуємо подію та закриваємо сокет */
            fprintf(stderr, "<4>Клієнт достроково розірвав TCP-з'єднання\n");
        }
    }
    return res;
}

/* Ініціалізація глобального ігнорування SIGPIPE */
void init_signal_protection(void) {
    struct sigaction sa;
    sa.sa_handler = SIG_IGN;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;
    sigaction(SIGPIPE, &sa, NULL);
}
