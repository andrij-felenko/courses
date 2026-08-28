/* iotest.c — стенд «чи діє ionice», два режими в одній програмі.
 *   cc -O2 -pthread -o iotest iotest.c
 *   ./iotest meter <файл> <секунд>
 *   ./iotest load  <файл> <клас> <рівень> <потоків> <секунд>
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <pthread.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/syscall.h>
#include <time.h>
#include <unistd.h>

#define MBLK  4096u            /* читання вимірювача   */
#define LBLK  (64u * 1024u)    /* читання навантажувача */
#define BUCKS 2000             /* корзина 10 мкс, стеля 20 мс */

#define IOPRIO_WHO_PROCESS 1
#define IOPRIO_VALUE(cls, lvl) (((cls) << 13) | (lvl))

static int ioprio_set(int which, int who, int prio)
{
    return (int)syscall(SYS_ioprio_set, which, who, prio);
}

static uint64_t now_ns(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return (uint64_t)t.tv_sec * 1000000000ull + (uint64_t)t.tv_nsec;
}

/* власний генератор: без блокувань і без звертань до ядра */
static uint64_t xorshift(uint64_t *s)
{
    *s ^= *s << 13; *s ^= *s >> 7; *s ^= *s << 17;
    return *s;
}

static int open_direct(const char *path, unsigned blk, uint64_t *blocks)
{
    int fd = open(path, O_RDONLY | O_DIRECT);
    if (fd < 0) { perror("open O_DIRECT"); exit(1); }
    off_t sz = lseek(fd, 0, SEEK_END);
    if (sz < (off_t)blk * 1024) { fprintf(stderr, "файл замалий\n"); exit(1); }
    *blocks = (uint64_t)sz / blk;
    return fd;
}

static double pct(const uint32_t *hist, uint64_t n, double p)
{
    uint64_t need = (uint64_t)(n * p), acc = 0;
    for (int i = 0; i <= BUCKS; i++) {
        acc += hist[i];
        if (acc >= need) return i * 10.0 + 5.0;   /* середина корзини */
    }
    return -1.0;
}

static void meter(const char *path, int seconds)
{
    uint64_t blocks;
    int fd = open_direct(path, MBLK, &blocks);
    void *buf;
    if (posix_memalign(&buf, MBLK, MBLK)) { perror("posix_memalign"); exit(1); }

    uint32_t *hist = calloc(BUCKS + 1, sizeof *hist);
    uint64_t seed = now_ns() | 1, n = 0;
    uint64_t stop = now_ns() + (uint64_t)seconds * 1000000000ull;

    while (now_ns() < stop) {
        off_t off = (off_t)((xorshift(&seed) % blocks) * MBLK);
        uint64_t t0 = now_ns();
        if (pread(fd, buf, MBLK, off) != (ssize_t)MBLK) { perror("pread"); exit(1); }
        uint64_t bucket = (now_ns() - t0) / 1000 / 10;
        hist[bucket < BUCKS ? bucket : BUCKS]++;
        n++;
    }
    if (n == 0) { fprintf(stderr, "жодної проби\n"); exit(1); }

    printf("проб %-8llu медіана %6.0f мкс   p99 %7.0f мкс   за стелею %.2f%%\n",
           (unsigned long long)n, pct(hist, n, 0.50), pct(hist, n, 0.99),
           100.0 * hist[BUCKS] / (double)n);
    close(fd); free(buf); free(hist);
}

struct job { const char *path; uint64_t stop; int prio; int id; };

static void *worker(void *arg)
{
    struct job *j = arg;
    /* пріоритет — атрибут ЗАДАЧІ, тож кожен потік виставляє його собі сам */
    if (ioprio_set(IOPRIO_WHO_PROCESS, 0, j->prio) < 0) { perror("ioprio_set"); exit(1); }

    uint64_t blocks;
    int fd = open_direct(j->path, LBLK, &blocks);
    void *buf;
    if (posix_memalign(&buf, MBLK, LBLK)) { perror("posix_memalign"); exit(1); }
    uint64_t seed = now_ns() + 0x9E3779B97F4A7C15ull * (uint64_t)(j->id + 1);

    while (now_ns() < j->stop) {
        off_t off = (off_t)((xorshift(&seed) % blocks) * LBLK);
        if (pread(fd, buf, LBLK, off) < 0) { perror("pread"); exit(1); }
    }
    close(fd); free(buf);
    return NULL;
}

static void loader(const char *path, int cls, int lvl, int nthr, int seconds)
{
    int prio = IOPRIO_VALUE(cls, lvl);
    uint64_t stop = now_ns() + (uint64_t)seconds * 1000000000ull;
    if (ioprio_set(IOPRIO_WHO_PROCESS, 0, prio) < 0) { perror("ioprio_set"); exit(1); }

    struct job *jobs = calloc(nthr, sizeof *jobs);
    pthread_t *th = calloc(nthr, sizeof *th);
    for (int i = 0; i < nthr; i++) {
        jobs[i] = (struct job){ path, stop, prio, i };
        pthread_create(&th[i], NULL, worker, &jobs[i]);
    }
    for (int i = 0; i < nthr; i++) pthread_join(th[i], NULL);
    free(th); free(jobs);
}

int main(int argc, char **argv)
{
    if (argc == 4 && !strcmp(argv[1], "meter"))
        meter(argv[2], atoi(argv[3]));
    else if (argc == 7 && !strcmp(argv[1], "load"))
        loader(argv[2], atoi(argv[3]), atoi(argv[4]), atoi(argv[5]), atoi(argv[6]));
    else {
        fprintf(stderr, "%s meter <файл> <секунд>\n"
                        "%s load  <файл> <клас> <рівень> <потоків> <секунд>\n",
                argv[0], argv[0]);
        return 2;
    }
    return 0;
}
