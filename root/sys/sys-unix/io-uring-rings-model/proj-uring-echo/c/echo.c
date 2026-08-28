/* echo.c — ехо-сервер на io_uring
 * cc -O2 -o echo echo.c -luring        liburing ≥ 2.4, ядро ≥ 5.19
 */
#define _GNU_SOURCE
#include <liburing.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/socket.h>
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define PORT        9000
#define QD           256          /* глибина кільця подань        */
#define BUF_COUNT   1024          /* мусить бути степенем двійки  */
#define BUF_SIZE    2048
#define BGID           1          /* номер групи наданих буферів  */
#define MAX_CONN   16384          /* ≥ RLIMIT_NOFILE: індексуємо дескриптором */

enum { OP_ACCEPT, OP_RECV, OP_SEND };

/* user_data: верхній байт — що це було, молодші 32 біти — дескриптор */
#define UD(op, fd)  (((__u64)(op) << 56) | (__u32)(fd))
#define UD_OP(u)    ((int)((u) >> 56))
#define UD_FD(u)    ((int)(__u32)(u))

struct conn { int bid; unsigned off, left; };

static struct io_uring            ring;
static struct io_uring_buf_ring  *br;
static char                      *bufs;
static struct conn                conns[MAX_CONN];
static int    starved[MAX_CONN], n_starved;   /* кому забракло буфера */

static char *buf_at(int bid) { return bufs + (size_t)bid * BUF_SIZE; }

static void ring_setup(void)
{
    struct io_uring_params p;
    memset(&p, 0, sizeof p);
    p.flags = IORING_SETUP_SINGLE_ISSUER | IORING_SETUP_DEFER_TASKRUN;

    int ret = io_uring_queue_init_params(QD, &ring, &p);
    if (ret == -EINVAL) {                  /* ядро старше за 6.1 — без цих прапорців */
        memset(&p, 0, sizeof p);
        ret = io_uring_queue_init_params(QD, &ring, &p);
    }
    if (ret < 0) { fprintf(stderr, "queue_init: %s\n", strerror(-ret)); exit(1); }

    bufs = malloc((size_t)BUF_COUNT * BUF_SIZE);
    if (!bufs) { perror("malloc"); exit(1); }

    int err;
    br = io_uring_setup_buf_ring(&ring, BUF_COUNT, BGID, 0, &err);
    if (!br) { fprintf(stderr, "buf_ring: %s\n", strerror(-err)); exit(1); }

    int mask = io_uring_buf_ring_mask(BUF_COUNT);
    for (int i = 0; i < BUF_COUNT; i++)
        io_uring_buf_ring_add(br, buf_at(i), BUF_SIZE, i, mask, i);
    io_uring_buf_ring_advance(br, BUF_COUNT);   /* аж тепер ядро їх бачить */
}
