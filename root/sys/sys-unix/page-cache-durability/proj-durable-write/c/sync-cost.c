/* sync-cost.c — ціна кожного різновиду синхронізації і перевірка,
   чи скидав при цьому пристрій власний кеш.
   збірка: cc -O2 -Wall -Wextra -o sync-cost sync-cost.c
   запуск: ./sync-cost /каталог/на/справжньому/диску            */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <time.h>
#include <unistd.h>

enum { BLK = 4096, REPS = 200, PREFILL = 64, BIG = 64 << 20 };

static char blk[BLK];
static const char *DSTAT;                 /* шлях до лічильників диска */

static void die(const char *what) { perror(what); exit(1); }

static double now_ms(void)
{
    struct timespec ts;
    if (clock_gettime(CLOCK_MONOTONIC, &ts) != 0) die("clock_gettime");
    return ts.tv_sec * 1e3 + ts.tv_nsec / 1e6;
}

static int cmp_double(const void *a, const void *b)
{
    double x = *(const double *) a, y = *(const double *) b;
    return (x > y) - (x < y);
}

static double median(double *v, int n)
{
    qsort(v, n, sizeof *v, cmp_double);
    return (n & 1) ? v[n / 2] : (v[n / 2 - 1] + v[n / 2]) / 2;
}

/* Знайти файл лічильників ЦІЛОГО диска, на якому лежить шлях.
   Скидання кеша для розділів не рахуються, тому з розділу
   треба піднятися на крок угору.                                */
static int disk_stat_path(const char *path, char *out, size_t outsz)
{
    struct stat st;
    if (stat(path, &st) != 0) return errno;

    char node[128], probe[160];
    snprintf(node, sizeof node, "/sys/dev/block/%u:%u",
             major(st.st_dev), minor(st.st_dev));
    snprintf(probe, sizeof probe, "%s/partition", node);

    /* «..» після символьного посилання йде вгору від його ЦІЛІ:
       від …/nvme0n1p2 до …/nvme0n1, тобто до цілого диска.       */
    snprintf(out, outsz, "%s%s/stat", node,
             (access(probe, F_OK) == 0) ? "/.." : "");
    return 0;
}

struct dstat { unsigned long long writes, flushes, flush_ms; int fields; };

/* Рядок із сімнадцяти чисел:
     1 читань   2 злито  3 секторів  4 мс
     5 записів  6 злито  7 секторів  8 мс
     9 у роботі 10 мс вводу-виводу   11 зважені мс
    12–15 discard        16 скидань кеша    17 мс на скидання     */
static int read_dstat(const char *p, struct dstat *d)
{
    unsigned long long v[17] = { 0 };
    int n = 0;
    FILE *f = fopen(p, "r");
    if (!f) return errno;
    while (n < 17 && fscanf(f, "%llu", &v[n]) == 1) n++;
    fclose(f);

    d->fields   = n;
    d->writes   = (n >=  5) ? v[4]  : 0;
    d->flushes  = (n >= 16) ? v[15] : 0;
    d->flush_ms = (n >= 17) ? v[16] : 0;
    return (n >= 5) ? 0 : EINVAL;
}

/* Друкуємо не тільки час, а й приріст обох лічильників: скидання без
   жодного запису — це і є доказ, що fsync розмовляє з пристроєм навіть
   тоді, коли передавати нема чого.                                     */
static void report(const char *tag, double *t, int n,
                   const struct dstat *a, const struct dstat *b)
{
    printf("%-32s медіана %8.3f мс   записів: %-5llu скидань: %-5llu (на %d)\n",
           tag, median(t, n),
           b->writes - a->writes, b->flushes - a->flushes, n);
    fflush(stdout);
}

/* REPS разів «зміна + синхронізація». append: дописувати в кінець
   чи перезаписувати вже виділені блоки; datasync: fdatasync чи fsync. */
static void series(const char *tag, int fd, int append, int datasync)
{
    static double t[REPS];
    struct dstat a, b;

    read_dstat(DSTAT, &a);
    for (int i = 0; i < REPS; i++) {
        blk[0] = (char) i;                    /* щоб вміст справді мінявся */
        if (append) {
            if (write(fd, blk, BLK) != (ssize_t) BLK) die("write");
        } else {
            off_t off = (off_t) (i % PREFILL) * BLK;
            if (pwrite(fd, blk, BLK, off) != (ssize_t) BLK) die("pwrite");
        }
        double t0 = now_ms();
        int rc = datasync ? fdatasync(fd) : fsync(fd);
        double t1 = now_ms();
        if (rc != 0) die("sync");
        t[i] = t1 - t0;
    }
    read_dstat(DSTAT, &b);
    report(tag, t, REPS, &a, &b);
}

int main(int argc, char **argv)
{
    const char *dir = (argc > 1) ? argv[1] : ".";
    char dstat[512], path[4096];
    struct dstat probe, a, b;
    double t[REPS];

    if (disk_stat_path(dir, dstat, sizeof dstat) != 0) die("stat каталогу");
    DSTAT = dstat;
    if (read_dstat(DSTAT, &probe) != 0) {
        fprintf(stderr, "лічильники недоступні (%s): tmpfs, складений том "
                        "або каталог не на блоковому пристрої\n", dstat);
        return 1;
    }
    printf("лічильники: %s (%d полів%s)\n\n", dstat, probe.fields,
           probe.fields >= 17 ? "" : "; скидання НЕ рахуються — ядро до 5.5");

    snprintf(path, sizeof path, "%s/sync-cost.dat", dir);
    int fd = open(path, O_RDWR | O_CREAT | O_TRUNC, 0600);
    if (fd < 0) die(path);

    /* Псевдовипадковий вміст, а не нулі: на файловій системі зі
       стисненням блок із нулів до носія майже не доходить, і міряти
       не було б чого.                                  (xorshift64) */
    unsigned long long s = 88172645463325252ULL;
    for (size_t i = 0; i < sizeof blk; i++) {
        s ^= s << 13; s ^= s >> 7; s ^= s << 17;
        blk[i] = (char) s;
    }

    /* А. fsync над файлом, у якому від попереднього fsync не змінилося
          нічого. Роботи для носія тут немає — лишається сама розмова
          з пристроєм.                                                 */
    if (fsync(fd) != 0) die("fsync");
    read_dstat(DSTAT, &a);
    for (int i = 0; i < REPS; i++) {
        double t0 = now_ms();
        if (fsync(fd) != 0) die("fsync");
        t[i] = now_ms() - t0;
    }
    read_dstat(DSTAT, &b);
    report("fsync без жодної зміни", t, REPS, &a, &b);

    /* Б. fsync після 64 МіБ у кеші: тут ціна — це швидкість носія. */
    for (int r = 0; r < 5; r++) {
        if (ftruncate(fd, 0) != 0) die("ftruncate");
        if (lseek(fd, 0, SEEK_SET) < 0) die("lseek");
        for (int i = 0; i < BIG / BLK; i++)
            if (write(fd, blk, BLK) != (ssize_t) BLK) die("write");
        double t0 = now_ms();
        if (fsync(fd) != 0) die("fsync");
        t[r] = now_ms() - t0;
    }
    printf("%-32s медіана %8.3f мс\n", "fsync після 64 МіБ у кеші",
           median(t, 5));

    /* В. Перезаписові потрібен файл, у якому блоки вже виділені. */
    if (ftruncate(fd, 0) != 0) die("ftruncate");
    if (lseek(fd, 0, SEEK_SET) < 0) die("lseek");
    for (int i = 0; i < PREFILL; i++)
        if (write(fd, blk, BLK) != (ssize_t) BLK) die("write");
    if (fsync(fd) != 0) die("fsync");

    series("перезапис 4 КіБ + fdatasync",   fd, 0, 1);
    series("перезапис 4 КіБ + fsync",       fd, 0, 0);

    if (lseek(fd, 0, SEEK_END) < 0) die("lseek");
    series("дописування 4 КіБ + fdatasync", fd, 1, 1);
    series("дописування 4 КіБ + fsync",     fd, 1, 0);

    close(fd);
    unlink(path);
    return 0;
}
