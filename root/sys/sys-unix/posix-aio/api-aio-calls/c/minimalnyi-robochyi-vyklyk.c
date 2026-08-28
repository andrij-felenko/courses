#include <aio.h>
#include <errno.h>
#include <fcntl.h>
#include <signal.h>      /* SIGEV_*: glibc віддає їх і через <aio.h>, POSIX — звідси */
#include <stdio.h>
#include <string.h>
#include <unistd.h>

#define N   4
#define BLK 4096

int main(void)
{
    int fd = open("data.bin", O_RDONLY);
    if (fd < 0) { perror("open"); return 1; }

    /* блоки й буфери мусять пережити виклик, тому не в кадрі, що зникне */
    static struct aiocb cb[N];
    static char         buf[N][BLK];
    const struct aiocb *list[N];

    for (int i = 0; i < N; i++) {
        memset(&cb[i], 0, sizeof cb[i]);          /* обнулення — умова контракту */
        cb[i].aio_fildes = fd;
        cb[i].aio_buf    = buf[i];
        cb[i].aio_nbytes = BLK;
        cb[i].aio_offset = (off_t)i * BLK;        /* абсолютне зміщення */
        cb[i].aio_sigevent.sigev_notify = SIGEV_NONE;
        list[i] = &cb[i];
        if (aio_read(&cb[i]) == -1) { perror("aio_read"); return 1; }
    }

    for (int left = N; left > 0; ) {
        if (aio_suspend(list, N, NULL) == -1 && errno != EINTR) {
            perror("aio_suspend");                /* EAGAIN не буває: timeout = NULL */
            return 1;
        }
        for (int i = 0; i < N; i++) {
            if (list[i] == NULL) continue;        /* результат уже забрано */
            int e = aio_error(&cb[i]);
            if (e == EINPROGRESS) continue;
            ssize_t n = aio_return(&cb[i]);       /* рівно один раз на запит */
            if (n == -1) fprintf(stderr, "запит %d: %s\n", i, strerror(e));
            else         printf("запит %d: %zd байтів\n", i, n);
            list[i] = NULL;                       /* NULL у списку дозволено */
            left--;
        }
    }
    close(fd);                                    /* лише коли забрано все */
    return 0;
}
