/* copyfd.c — переливає байти з одного дескриптора в інший.
   Збірка:  cc -O2 -Wall -Wextra -o copyfd copyfd.c
   Запуск:  ./copyfd [вхід|-] [вихід|-]                        */

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define BUFSZ (64 * 1024)

/* Приспати процес, доки дескриптор не стане готовим.
   Повертає −1 лише на справжній помилці очікування.        */
static int wait_ready(int fd, short what)
{
    struct pollfd pf;
    pf.fd = fd;
    pf.events = what;
    pf.revents = 0;
    if (poll(&pf, 1, -1) < 0 && errno != EINTR)
        return -1;
    return 0;
}

/* Дописати РІВНО n байтів. 0 — усе дописано, −1 — errno виставлено. */
static int write_all(int fd, const char *p, size_t n)
{
    while (n > 0) {
        ssize_t m = write(fd, p, n);
        if (m < 0) {
            if (errno == EINTR)
                continue;                  /* сигнал: не записано нічого */
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                if (wait_ready(fd, POLLOUT) < 0)
                    return -1;
                continue;                  /* місце звільнилося — ще раз */
            }
            return -1;                     /* EPIPE, ENOSPC, EIO — це кінець */
        }
        p += (size_t)m;                    /* хвіст, якого write не взяв */
        n -= (size_t)m;
    }
    return 0;
}

/* Перелити все з in у out. 0 — джерело вичерпано, −1 — errno виставлено. */
static int copy_fd(int in, int out)
{
    char buf[BUFSZ];
    for (;;) {
        ssize_t n = read(in, buf, sizeof buf);
        if (n == 0)
            return 0;                      /* джерело скінчилося */
        if (n < 0) {
            if (errno == EINTR)
                continue;
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                if (wait_ready(in, POLLIN) < 0)
                    return -1;
                continue;
            }
            return -1;
        }
        if (write_all(out, buf, (size_t)n) < 0)
            return -1;
    }
}

int main(int argc, char **argv)
{
    int in = STDIN_FILENO, out = STDOUT_FILENO;

    /* Без цього рядка запис у закритий канал тихо вбиває процес сигналом;
       з ним write чесно повертає −1 з errno == EPIPE.                    */
    signal(SIGPIPE, SIG_IGN);

    if (argc > 1 && strcmp(argv[1], "-") != 0) {
        in = open(argv[1], O_RDONLY);
        if (in < 0) { perror(argv[1]); return 1; }
    }
    if (argc > 2 && strcmp(argv[2], "-") != 0) {
        out = open(argv[2], O_WRONLY | O_CREAT | O_TRUNC, 0644);
        if (out < 0) { perror(argv[2]); return 1; }
    }

    if (copy_fd(in, out) < 0) { perror("copyfd"); return 1; }

    /* close теж повертає помилку — на мережевій файловій системі саме він
       повідомляє про невдалий відкладений запис. Ігнорувати не можна.    */
    if (out != STDOUT_FILENO && close(out) < 0) { perror("close"); return 1; }
    return 0;
}
