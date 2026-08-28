/* echod.c — echo-служба, яка вміє і підхопити переданий сокет, і зробити свій.
   Складання:  cc -O2 -Wall -o echod echod.c                                  */

#define _POSIX_C_SOURCE 200809L
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <netinet/in.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define LISTEN_FDS_START 3
#define FALLBACK_PORT    9000

/* Скільки сокетів передали САМЕ НАМ. Заразом прибираємо змінні з оточення,
   щоб вони не поїхали далі — до наших власних нащадків.                    */
static int listen_fds(void)
{
    const char *pid = getenv("LISTEN_PID");
    const char *cnt = getenv("LISTEN_FDS");
    char self[32];
    int n;

    if (!pid || !cnt)
        return 0;

    snprintf(self, sizeof self, "%ld", (long) getpid());
    if (strcmp(pid, self) != 0)
        return 0;                  /* змінні дісталися нам у спадок від предка */

    n = atoi(cnt);
    unsetenv("LISTEN_PID");
    unsetenv("LISTEN_FDS");
    unsetenv("LISTEN_FDNAMES");
    return n;
}

/* Друга гілка: менеджера немає — сокет робимо самі. */
static int listen_myself(int port)
{
    struct sockaddr_in a = { .sin_family = AF_INET,
                             .sin_port   = htons(port),
                             .sin_addr   = { htonl(INADDR_LOOPBACK) } };
    int fd = socket(AF_INET, SOCK_STREAM, 0);
    int on = 1;

    if (fd < 0)                                         { perror("socket"); exit(1); }
    setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof on);
    if (bind(fd, (struct sockaddr *) &a, sizeof a) < 0)  { perror("bind");   exit(1); }
    if (listen(fd, 128) < 0)                             { perror("listen"); exit(1); }
    return fd;
}

/* Одне з'єднання: усе прочитане повертаємо назад, поки клієнт не піде. */
static void echo(int c)
{
    char buf[4096];

    for (;;) {
        ssize_t n = read(c, buf, sizeof buf);

        if (n == 0) return;                       /* клієнт закрив свій бік */
        if (n < 0) { if (errno == EINTR) continue; return; }

        for (ssize_t off = 0; off < n; ) {
            ssize_t w = write(c, buf + off, n - off);
            if (w < 0) { if (errno == EINTR) continue; return; }
            off += w;
        }
    }
}

int main(void)
{
    int n = listen_fds();
    int lfd;

    signal(SIGPIPE, SIG_IGN);      /* клієнт може зникнути посеред відповіді */

    if (n > 1) {
        fprintf(stderr, "передано %d сокетів, а ми вміємо один\n", n);
        return 1;
    }
    lfd = (n == 1) ? LISTEN_FDS_START           /* уже прив'язаний і слухає */
                   : listen_myself(FALLBACK_PORT);
    fcntl(lfd, F_SETFD, FD_CLOEXEC);            /* нащадкам сокет не потрібен */

    for (;;) {
        int c = accept(lfd, NULL, NULL);

        if (c < 0) {
            if (errno == EINTR || errno == ECONNABORTED)
                continue;
            perror("accept");
            return 1;
        }
        echo(c);
        close(c);
    }
}
