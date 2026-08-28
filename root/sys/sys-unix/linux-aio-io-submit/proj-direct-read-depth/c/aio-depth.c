/* aio-depth.c — темп прямих читань 4 КіБ залежно від глибини черги.
 * збірка:  cc -O2 -o aio-depth aio-depth.c -laio
 * вжиток:  ./aio-depth data.bin             прямий ввід-вивід
 *          ./aio-depth data.bin buffered    те саме, але через кеш сторінок
 */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <libaio.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define BLK     4096        /* розмір одного читання */
#define MAXQD   256         /* стеля глибини в цій програмі */
#define WINDOW  3.0         /* секунд вимірювання на кожну глибину */

static const int depths[] = { 1, 8, 64 };

struct lab {
    int          fd;
    uint64_t     nblocks;       /* скільки блоків BLK уміщає файл */
    uint64_t     seed;
    char        *buf[MAXQD];    /* вирівняні буфери, по одному на слот */
    struct iocb  cb[MAXQD];     /* живі iocb: жоден не на стеку подавача */
    struct iocb *batch[MAXQD];  /* масив покажчиків, який приймає io_submit */
};

static double now(void)                 /* монотонний годинник: не стрибне */
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static uint64_t xorshift(uint64_t *s)   /* дешеве джерело випадкових блоків */
{
    *s ^= *s << 13;  *s ^= *s >> 7;  *s ^= *s << 17;
    return *s;
}

/* io_submit має право прийняти менше, ніж просили: досилаємо хвіст */
static int submit_all(io_context_t ctx, struct iocb **v, int n)
{
    int done = 0;
    while (done < n) {
        int r = io_submit(ctx, n - done, v + done);  /* libaio: помилка — це -errno */
        if (r < 0) {
            if (r == -EINTR || r == -EAGAIN)
                continue;                            /* тимчасово тісно — ще раз */
            fprintf(stderr, "io_submit: %s\n", strerror(-r));
            return -1;
        }
        done += r;
    }
    return 0;
}

/* зарядити слот новим читанням із випадкового блоку файлу */
static void arm(struct lab *l, int slot)
{
    off_t off = (off_t)(xorshift(&l->seed) % l->nblocks) * BLK;
    io_prep_pread(&l->cb[slot], l->fd, l->buf[slot], BLK, off);
    l->cb[slot].data = (void *)(uintptr_t)slot;  /* ПІСЛЯ prep: він робить memset */
}

static double measure(struct lab *l, int depth)
{
    struct io_event ev[MAXQD];
    io_context_t ctx = 0;          /* io_setup вимагає нуля, інакше EINVAL */
    long long done = 0;
    int inflight, filling = 1, i, k, n, rc;
    double t0, t1;

    rc = io_setup(depth, &ctx);
    if (rc < 0) {
        fprintf(stderr, "io_setup: %s\n", strerror(-rc));
        return -1;
    }
    for (i = 0; i < depth; i++) {
        arm(l, i);
        l->batch[i] = &l->cb[i];
    }

    t0 = t1 = now();
    if (submit_all(ctx, l->batch, depth) < 0) {
        io_destroy(ctx);
        return -1;
    }
    inflight = depth;

    while (inflight > 0) {
        n = io_getevents(ctx, 1, depth, ev, NULL);   /* чекати щонайменше на одне */
        if (n < 0) {
            if (n == -EINTR)
                continue;
            fprintf(stderr, "io_getevents: %s\n", strerror(-n));
            break;
        }
        inflight -= n;
        for (k = 0; k < n; k++) {
            long res = (long)ev[k].res;              /* у libaio поле беззнакове */
            if (res != BLK) {
                fprintf(stderr, "читання не вдалося: %s\n",
                        res < 0 ? strerror((int)-res) : "неповний результат");
                io_destroy(ctx);                     /* дочекається решти запитів */
                return -1;
            }
            if (filling)
                done++;
        }
        if (!filling)
            continue;                   /* вікно скінчилося: лише добираємо політ */
        if (now() - t0 >= WINDOW) {
            t1 = now();
            filling = 0;
            continue;
        }
        for (k = 0; k < n; k++) {       /* на місце кожного завершеного — новий */
            int slot = (int)(uintptr_t)ev[k].data;
            arm(l, slot);
            l->batch[k] = &l->cb[slot];
        }
        if (submit_all(ctx, l->batch, n) < 0)
            break;
        inflight += n;
    }

    io_destroy(ctx);
    return t1 > t0 ? (double)done / (t1 - t0) : -1;
}

int main(int argc, char **argv)
{
    struct lab l;
    struct stat st;
    int direct = 1, i;

    if (argc < 2) {
        fprintf(stderr, "вжиток: %s <файл> [buffered]\n", argv[0]);
        return 2;
    }
    if (argc > 2 && strcmp(argv[2], "buffered") == 0)
        direct = 0;

    memset(&l, 0, sizeof l);
    l.seed = 0x9e3779b97f4a7c15ULL;

    l.fd = open(argv[1], O_RDONLY | (direct ? O_DIRECT : 0));
    if (l.fd < 0) { perror("open"); return 1; }
    if (fstat(l.fd, &st) < 0) { perror("fstat"); return 1; }

    l.nblocks = (uint64_t)st.st_size / BLK;
    if (l.nblocks < 256 * 1024) {          /* менше за гігабайт — міряти нема сенсу */
        fprintf(stderr, "файл замалий: потрібен щонайменше 1 ГіБ даних\n");
        return 1;
    }
    for (i = 0; i < MAXQD; i++)
        if (posix_memalign((void **)&l.buf[i], BLK, BLK) != 0) {
            fprintf(stderr, "posix_memalign: не вистачило пам'яті\n");
            return 1;
        }

    printf("%s, читання по %d Б\n", direct ? "O_DIRECT" : "через кеш", BLK);
    printf("глибина    операцій/с       МіБ/с\n");
    for (i = 0; i < (int)(sizeof depths / sizeof depths[0]); i++) {
        double r = measure(&l, depths[i]);
        if (r < 0)
            return 1;
        printf("%7d %13.0f %11.1f\n",
               depths[i], r, r * BLK / (1024.0 * 1024.0));
    }
    close(l.fd);
    return 0;
}
