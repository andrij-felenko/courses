/* rabench.c — стенд випереджувального читання.
   збірка: cc -O2 -Wall -Wextra -o rabench rabench.c
   запуск: ./rabench <файл> <обхід> <порада> <блок_байтів> <блоків|0=усі>
     обхід : seq | rand | mseq | mrand    (m* — через відображення в пам'ять)
     порада: none | normal | sequential | random | direct                     */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <time.h>
#include <unistd.h>

/* ── Годинник: лише монотонний ─────────────────────────────────────────── */
static uint64_t now_ns(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (uint64_t) ts.tv_sec * 1000000000ull + (uint64_t) ts.tv_nsec;
}

/* ── Лічильники завдання: /proc/self/io ─────────────────────────────────── */
struct io_ctr { unsigned long long rchar, syscr, read_bytes; };

static void read_io_ctr(struct io_ctr *c)
{
    char key[64];
    unsigned long long v;
    FILE *f = fopen("/proc/self/io", "r");

    memset(c, 0, sizeof *c);
    if (!f) return;                     /* ядро без обліку — лишаємо нулі */
    while (fscanf(f, " %63[^:]: %llu", key, &v) == 2) {
        if      (!strcmp(key, "rchar"))      c->rchar      = v;
        else if (!strcmp(key, "syscr"))      c->syscr      = v;
        else if (!strcmp(key, "read_bytes")) c->read_bytes = v;
    }
    fclose(f);
}

/* ── Лічильники пристрою: /sys/dev/block/<major>:<minor>/stat ───────────── */
struct dev_ctr { unsigned long long reads, merges, sectors; };

static void read_dev_ctr(const char *path, struct dev_ctr *c)
{
    FILE *f = fopen(path, "r");

    memset(c, 0, sizeof *c);
    if (!f) return;
    if (fscanf(f, "%llu %llu %llu", &c->reads, &c->merges, &c->sectors) != 3)
        memset(c, 0, sizeof *c);
    fclose(f);
}

/* ── Вистудити кеш САМЕ ЦЬОГО файлу ─────────────────────────────────────── */
static int cool_file(int fd)
{
    /* Брудні сторінки на прохання не звільняються — спершу їх треба
       записати. На дескрипторі, відкритому лише для читання, fsync
       у Linux працює; відмова іншої системи тут не привід спинятися. */
    (void) fsync(fd);
    /* posix_fadvise ПОВЕРТАЄ номер помилки й НЕ чіпає errno:
       звична перевірка «< 0» тут мовчки пропустить збій.            */
    return posix_fadvise(fd, 0, 0, POSIX_FADV_DONTNEED);
}

/* ── Скільки сторінок файлу лишилося в пам'яті ─────────────────────────── */
static long resident_pages(int fd, off_t size)
{
    long ps = sysconf(_SC_PAGESIZE);
    size_t npages = (size_t) ((size + ps - 1) / ps), i;
    unsigned char *vec;
    void *map;
    long n = 0;

    /* mincore лише питає про стан сторінок і не тягне жодної з носія. */
    map = mmap(NULL, (size_t) size, PROT_READ, MAP_SHARED, fd, 0);
    if (map == MAP_FAILED) return -1;
    vec = malloc(npages);
    if (!vec) { munmap(map, (size_t) size); return -1; }
    if (mincore(map, (size_t) size, vec) == 0)
        for (i = 0; i < npages; i++) n += (vec[i] & 1);
    else
        n = -1;
    free(vec);
    munmap(map, (size_t) size);
    return n;
}

/* ── Порядок обходу: справжня перестановка з відтворюваним зерном ───────── */
static uint64_t rng = 0x9e3779b97f4a7c15ull;

static uint64_t xorshift64(void)
{
    uint64_t x = rng;
    x ^= x << 13; x ^= x >> 7; x ^= x << 17;
    return rng = x;
}

static uint32_t *permutation(size_t n)
{
    uint32_t *a = malloc(n * sizeof *a);
    size_t i;

    if (!a) return NULL;
    for (i = 0; i < n; i++) a[i] = (uint32_t) i;
    for (i = n; i > 1; i--) {                    /* тасування Фішера–Йейтса */
        size_t j = (size_t) (xorshift64() % i);
        uint32_t t = a[i - 1]; a[i - 1] = a[j]; a[j] = t;
    }
    return a;
}

int main(int argc, char **argv)
{
    const char *path, *walk, *hint;
    int fd, flags = O_RDONLY, is_rand, is_mmap, rc, advice = -1;
    size_t bs, want, nblocks, i;
    off_t size;
    struct stat st;
    struct io_ctr io0, io1;
    struct dev_ctr dv0, dv1;
    char devpath[64];
    unsigned char *buf = NULL;
    char *map = NULL;
    uint32_t *order = NULL;
    unsigned long long sink = 0, useful, reqs;
    uint64_t t0, t1;
    double sec;
    long left;

    if (argc != 6) {
        fprintf(stderr, "запуск: %s <файл> seq|rand|mseq|mrand "
                "none|normal|sequential|random|direct <блок_байтів> <блоків|0>\n",
                argv[0]);
        return 2;
    }
    path = argv[1]; walk = argv[2]; hint = argv[3];
    bs   = (size_t) strtoull(argv[4], NULL, 10);
    want = (size_t) strtoull(argv[5], NULL, 10);

    is_mmap = (walk[0] == 'm');
    is_rand = !strcmp(walk, "rand") || !strcmp(walk, "mrand");

    if (!strcmp(hint, "direct")) {
        if (is_mmap) {
            fprintf(stderr, "O_DIRECT і відображення не поєднуються\n"); return 2;
        }
        /* Вирівнювання — за логічним блоком пристрою (queue/logical_block_size).
           512 підходить майже скрізь; на 4Kn-носіях pread поверне EINVAL.      */
        if (bs % 512) { fprintf(stderr, "для O_DIRECT блок кратний 512\n"); return 2; }
        flags |= O_DIRECT;
    }

    fd = open(path, flags);
    if (fd < 0) { perror("open"); return 1; }
    if (fstat(fd, &st) != 0) { perror("fstat"); return 1; }
    size    = st.st_size;
    nblocks = (size_t) (size / (off_t) bs);
    if (want == 0 || want > nblocks) want = nblocks;
    snprintf(devpath, sizeof devpath, "/sys/dev/block/%u:%u/stat",
             major(st.st_dev), minor(st.st_dev));

    /* Перестановку будуємо ДО вистуджування: вона їсть і час, і пам'ять,
       а ні того, ні того в замір потрапити не повинно.                  */
    if (is_rand && !(order = permutation(nblocks))) {
        fprintf(stderr, "не вистачило пам'яті на перестановку\n"); return 1;
    }

    rc = cool_file(fd);
    if (rc) fprintf(stderr, "увага: вистудити не вдалося: %s\n", strerror(rc));
    left = resident_pages(fd, size);

    if (is_mmap) {
        map = mmap(NULL, (size_t) size, PROT_READ, MAP_SHARED, fd, 0);
        if (map == MAP_FAILED) { perror("mmap"); return 1; }
        if      (!strcmp(hint, "normal"))     advice = MADV_NORMAL;
        else if (!strcmp(hint, "sequential")) advice = MADV_SEQUENTIAL;
        else if (!strcmp(hint, "random"))     advice = MADV_RANDOM;
        if (advice >= 0 && madvise(map, (size_t) size, advice) != 0)
            perror("madvise");
    } else {
        if      (!strcmp(hint, "normal"))     advice = POSIX_FADV_NORMAL;
        else if (!strcmp(hint, "sequential")) advice = POSIX_FADV_SEQUENTIAL;
        else if (!strcmp(hint, "random"))     advice = POSIX_FADV_RANDOM;
        if (advice >= 0 && (rc = posix_fadvise(fd, 0, 0, advice)) != 0)
            fprintf(stderr, "увага: пораду не прийнято: %s\n", strerror(rc));
        if (flags & O_DIRECT) {
            void *p;
            if (posix_memalign(&p, 4096, bs)) {
                fprintf(stderr, "немає вирівняного буфера\n"); return 1;
            }
            buf = p;
        } else if (!(buf = malloc(bs))) {
            fprintf(stderr, "немає буфера\n"); return 1;
        }
    }

    read_io_ctr(&io0);
    read_dev_ctr(devpath, &dv0);
    t0 = now_ns();

    for (i = 0; i < want; i++) {
        off_t off = (off_t) (is_rand ? order[i] : i) * (off_t) bs;
        if (is_mmap) {
            size_t k;                     /* по дотику на сторінку блока */
            for (k = 0; k < bs; k += 4096) sink += (unsigned char) map[off + k];
        } else {
            /* pread, а не read: зсув у виклику, тож ніщо не залежить
               від поточної позиції — а стан здогаду однаково спільний,
               бо дескриптор той самий.                               */
            ssize_t n = pread(fd, buf, bs, off);
            if (n < 0) { perror("pread"); return 1; }
            if (n == 0) break;
            sink += buf[0];
        }
    }

    t1 = now_ns();
    read_io_ctr(&io1);
    read_dev_ctr(devpath, &dv1);

    sec    = (t1 - t0) / 1e9;
    useful = (unsigned long long) want * bs;
    reqs   = dv1.reads - dv0.reads;

    printf("%s / %s: блок %zu Б, блоків %zu, файл %.1f ГіБ\n",
           walk, hint, bs, want, size / 1073741824.0);
    printf("  час                 %9.3f с    корисних %8.1f МіБ/с\n",
           sec, useful / 1048576.0 / sec);
    printf("  rchar               %9.1f МіБ  за %llu викликів\n",
           (io1.rchar - io0.rchar) / 1048576.0, io1.syscr - io0.syscr);
    printf("  read_bytes          %9.1f МіБ  узято з носія\n",
           (io1.read_bytes - io0.read_bytes) / 1048576.0);
    printf("  надлишок            %9.2f×    з носія / корисного\n",
           (double) (io1.read_bytes - io0.read_bytes) / (double) useful);
    printf("  запитів до пристрою %9llu     середній %.1f КіБ\n", reqs,
           reqs ? (dv1.sectors - dv0.sectors) * 512.0 / reqs / 1024.0 : 0.0);
    printf("  у пам'яті перед прогоном: %ld сторінок файлу\n", left);
    fprintf(stderr, "# %llu\n", sink);   /* щоб читання не викинув оптимізатор */

    if (map) munmap(map, (size_t) size);
    free(buf); free(order); close(fd);
    return 0;
}
