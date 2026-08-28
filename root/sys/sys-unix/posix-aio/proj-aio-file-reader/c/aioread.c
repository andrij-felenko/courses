/* aioread.c — пачка читань через POSIX AIO і два заміри до неї
 * cc -O2 -o aioread aioread.c -lrt -pthread
 */
#define _GNU_SOURCE
#include <aio.h>
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define BLK    4096          /* і розмір запиту, і вирівнювання під O_DIRECT */
#define NREQ    256
#define MAXFD    64

struct batch {
    struct aiocb **cb;       /* масив ПОКАЖЧИКІВ — саме його хоче lio_listio */
    char         **buf;
    int            n;
};

static struct batch *batch_make(const int *fd, int nfd, int n, off_t nblocks)
{
    struct batch *b = malloc(sizeof *b);
    b->n   = n;
    b->cb  = calloc(n, sizeof *b->cb);
    b->buf = calloc(n, sizeof *b->buf);

    for (int i = 0; i < n; i++) {
        struct aiocb *c = calloc(1, sizeof *c);          /* купа, не стек */
        if (posix_memalign((void **)&b->buf[i], BLK, BLK) != 0)
            { perror("posix_memalign"); exit(1); }

        c->aio_fildes     = fd[i % nfd];                  /* розкладка по чергах */
        c->aio_offset     = (off_t)(((long)i * 9973) % nblocks) * BLK;
        c->aio_buf        = b->buf[i];
        c->aio_nbytes     = BLK;
        c->aio_lio_opcode = LIO_READ;
        c->aio_sigevent.sigev_notify = SIGEV_NONE;        /* питатимемо самі */
        b->cb[i] = c;
    }
    return b;
}
