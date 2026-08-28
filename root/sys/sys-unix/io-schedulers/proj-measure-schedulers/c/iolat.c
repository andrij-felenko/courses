/* iolat.c — затримка дрібних читань під фоновою заливкою запису
 *   збірка: cc -O2 -D_GNU_SOURCE iolat.c -o iolat -lpthread -lm
 *   запуск: ./iolat <файл-для-читання> <файл-для-запису> <секунд>      */
#include <fcntl.h>
#include <math.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define READ_BLK    4096u             /* дрібне читання — те, що болить  */
#define WRITE_BLK   (1u << 20)        /* заливка великими шматками       */
#define WRITE_FILE  (4ull << 30)      /* пишемо по колу, щоб не з'їсти диск */
#define WARMUP_NS   2000000000ull     /* перші дві секунди відкидаємо    */
#define MAX_SAMPLES 4000000u          /* 32 МБ під масив вимірів         */

static atomic_int      stop_flag;
static _Atomic uint64_t written;

static uint64_t now_ns(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (uint64_t)t.tv_sec * 1000000000ull + (uint64_t)t.tv_nsec;
}

static uint64_t rnd(uint64_t *s) {            /* splitmix64: дешево й рівно */
    uint64_t z = (*s += 0x9E3779B97F4A7C15ull);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}

/* Вирівнювання для O_DIRECT питаємо в ядра, а не вгадуємо.
   STATX_DIOALIGN є з Linux 6.1; де немає — 4096 безпечне і для 512e, і для 4Kn. */
static size_t dio_align(int fd) {
#ifdef STATX_DIOALIGN
    struct statx st;
    if (statx(fd, "", AT_EMPTY_PATH, STATX_DIOALIGN, &st) == 0 &&
        (st.stx_mask & STATX_DIOALIGN) && st.stx_dio_offset_align) {
        size_t a = st.stx_dio_offset_align;
        if (st.stx_dio_mem_align > a) a = st.stx_dio_mem_align;
        return a;
    }
#endif
    return 4096;
}

static void *flooder(void *arg) {
    int fd = open((const char *)arg, O_WRONLY | O_CREAT, 0644);
    if (fd < 0) { perror("open write"); return NULL; }
    char *buf = malloc(WRITE_BLK);
    memset(buf, 0xA5, WRITE_BLK);
    uint64_t off = 0;
    while (!atomic_load_explicit(&stop_flag, memory_order_relaxed)) {
        ssize_t n = pwrite(fd, buf, WRITE_BLK, (off_t)off);
        if (n <= 0) break;
        atomic_fetch_add(&written, (uint64_t)n);
        off = (off + (uint64_t)n) % WRITE_FILE;
        /* штовхаємо накопичене на носій, не чекаючи на нього:
           це і є фоновий зворотний запис, проти якого воюють планувальники */
        if (off != 0 && off % (64ull << 20) == 0)
            sync_file_range(fd, (off_t)(off - (64ull << 20)),
                            64ll << 20, SYNC_FILE_RANGE_WRITE);
    }
    free(buf);
    close(fd);
    return NULL;
}

static int cmp_u64(const void *a, const void *b) {
    uint64_t x = *(const uint64_t *)a, y = *(const uint64_t *)b;
    return (x > y) - (x < y);
}

static double pct_us(const uint64_t *v, size_t n, double p) {
    size_t i = (size_t)ceil(p / 100.0 * (double)n);   /* найближчий ранг */
    if (i < 1) i = 1;
    if (i > n) i = n;
    return (double)v[i - 1] / 1000.0;
}

int main(int argc, char **argv) {
    if (argc != 4) {
        fprintf(stderr, "usage: %s <read-file> <write-file> <seconds>\n", argv[0]);
        return 2;
    }
    unsigned secs = (unsigned)strtoul(argv[3], NULL, 10);

    int fd = open(argv[1], O_RDONLY | O_DIRECT);
    if (fd < 0) { perror("open read (O_DIRECT)"); return 1; }
    off_t  size  = lseek(fd, 0, SEEK_END);
    size_t align = dio_align(fd);
    size_t blk   = READ_BLK < align ? align : READ_BLK;
    if (size < (off_t)(blk * 262144)) {          /* хоч гігабайт, а краще більше */
        fprintf(stderr, "файл замалий: читання мають розбігтися по носію\n");
        return 1;
    }
    void *buf = NULL;
    if (posix_memalign(&buf, align, blk)) { perror("posix_memalign"); return 1; }

    uint64_t *lat = malloc((size_t)MAX_SAMPLES * sizeof *lat);
    size_t    n = 0;
    uint64_t  nblocks = (uint64_t)size / blk;
    uint64_t  seed = now_ns();

    pthread_t th;
    pthread_create(&th, NULL, flooder, argv[2]);

    uint64_t t0 = now_ns();
    uint64_t deadline = t0 + (uint64_t)secs * 1000000000ull;
    uint64_t warm = t0 + WARMUP_NS, t_first = 0;
    for (;;) {
        uint64_t a = now_ns();
        if (a >= deadline || n == MAX_SAMPLES) break;
        off_t off = (off_t)((rnd(&seed) % nblocks) * blk);
        ssize_t r = pread(fd, buf, blk, off);
        uint64_t b = now_ns();
        if (r != (ssize_t)blk) { perror("pread"); break; }
        if (a >= warm) { if (!t_first) t_first = a; lat[n++] = b - a; }
    }
    uint64_t t_end = now_ns();
    atomic_store(&stop_flag, 1);
    pthread_join(th, NULL);

    if (n < 1000) { fprintf(stderr, "замало вимірів\n"); return 1; }
    qsort(lat, n, sizeof *lat, cmp_u64);
    double span = (double)(t_end - t_first) / 1e9;
    printf("%8.0f %8.0f %8.0f %8.0f %9.0f %8.1f\n",
           pct_us(lat, n, 50), pct_us(lat, n, 99), pct_us(lat, n, 99.9),
           (double)lat[n - 1] / 1000.0,
           (double)n / span,
           (double)atomic_load(&written) / (1u << 20) /
               ((double)(t_end - t0) / 1e9));
    return 0;
}
