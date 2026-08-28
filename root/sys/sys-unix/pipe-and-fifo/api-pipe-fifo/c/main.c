#define _GNU_SOURCE
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <signal.h>

void handle(const char *cmd, size_t len);   /* розбір команди — не про цю довідку */

int main(void)
{
    const char *path = "/tmp/commands";

    /* 1. Запис у каталозі. Уже існує — не помилка, а звичайна річ. */
    if (mkfifo(path, 0600) == -1 && errno != EEXIST)
        return 1;

    /* 2. O_RDWR: власний кінець на запис тримає лічильник записувачів
          ненульовим, тож read не поверне 0, коли останній клієнт відійде.
          Ціна — переносности немає, POSIX цього не визначає. */
    int fd = open(path, O_RDWR | O_CLOEXEC);
    if (fd == -1)
        return 1;

    /* 3. Відповіді ми пишемо в інші канали — SIGPIPE не має нас убивати. */
    signal(SIGPIPE, SIG_IGN);

    for (;;) {
        char    buf[4096];             /* PIPE_BUF: клієнтський запис приходить цілим */
        ssize_t n = read(fd, buf, sizeof buf);

        if (n > 0) {
            handle(buf, (size_t)n);
            continue;
        }
        if (n == -1 && errno == EINTR)
            continue;                  /* сигнал — просто повторити */
        break;                         /* справжня помилка; n == 0 тут неможливе */
    }

    close(fd);
    return 0;
}
