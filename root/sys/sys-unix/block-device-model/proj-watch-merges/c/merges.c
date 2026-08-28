/* merges.c — скільки запитів насправді доїхало до носія.
   збірка: cc -O2 -Wall -o merges merges.c
   запуск: sudo ./merges /var/tmp/scratch.bin sda            */

#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define REC   4096ull                 /* один запис */
#define NREC  65536ull                /* 65536 × 4 КіБ = 256 МіБ на прохід */
#define SPAN  (REC * NREC)
#define SKIP  4097ull                 /* непарний → обходить усі слоти рівно раз */

struct dstat { unsigned long long ios, merges, sectors, ticks; };

/* /sys/block/<dev>/stat: 17 полів; поля 5–8 — це запис:
   запити, злиття, сектори (завжди по 512 Б), очікування в мс */
static int read_stat(const char *dev, struct dstat *s)
{
    char path[256];
    unsigned long long v[17] = { 0 };
    int n = 0;

    snprintf(path, sizeof path, "/sys/block/%s/stat", dev);
    FILE *f = fopen(path, "r");
    if (!f)
        return -1;
    while (n < 17 && fscanf(f, "%llu", &v[n]) == 1)
        n++;
    fclose(f);
    if (n < 8)
        return -1;
    s->ios = v[4]; s->merges = v[5]; s->sectors = v[6]; s->ticks = v[7];
    return 0;
}

/* один прохід: NREC записів по REC байтів у ту саму область.
   base — зсув усього потоку (0 або 512);
   skip — крок у слотах: 1 = слот за слотом, SKIP = вроздріб */
static void one_pass(int fd, const void *buf,
                     unsigned long long base, unsigned long long skip)
{
    for (unsigned long long i = 0; i < NREC; i++) {
        unsigned long long slot = (i * skip) % NREC;
        off_t off = (off_t)(base + slot * REC);

        if (pwrite(fd, buf, REC, off) != (ssize_t)REC) {
            fprintf(stderr, "pwrite на зсуві %lld: %s\n",
                    (long long)off, strerror(errno));
            exit(1);
        }
    }
}

/* printf міряє ширину в байтах, а назви проходів — кирилицею */
static void put_label(const char *s)
{
    int chars = 0;

    for (const unsigned char *q = (const unsigned char *)s; *q; q++)
        if ((*q & 0xC0) != 0x80)
            chars++;
    fputs(s, stdout);
    while (chars++ < 22)
        putchar(' ');
}

static void measure(const char *label, int fd, const void *buf,
                    const char *dev, unsigned long long base,
                    unsigned long long skip)
{
    struct dstat a, b;
    struct timespec t0, t1;

    sync();                                    /* хай чуже доїде до носія */
    if (read_stat(dev, &a)) { perror("stat"); exit(1); }
    clock_gettime(CLOCK_MONOTONIC, &t0);

    one_pass(fd, buf, base, skip);
    if (fsync(fd)) { perror("fsync"); exit(1); }

    clock_gettime(CLOCK_MONOTONIC, &t1);
    if (read_stat(dev, &b)) { perror("stat"); exit(1); }

    unsigned long long ios  = b.ios     - a.ios;
    unsigned long long mrg  = b.merges  - a.merges;
    unsigned long long sect = b.sectors - a.sectors;
    double sec = (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec) / 1e9;

    put_label(label);
    printf("%8llu %9llu %9.1f %10.1f %9.2f\n",
           ios, mrg,
           sect / 2048.0,                       /* сектори по 512 Б → МіБ */
           ios ? sect / 2.0 / ios : 0.0,        /* середній запит, КіБ */
           sec);
}

int main(int argc, char **argv)
{
    if (argc != 3) {
        fprintf(stderr, "вжиток: %s <порожній файл або пристрій> <ім'я в /sys/block>\n",
                argv[0]);
        return 2;
    }

    void *buf;
    if (posix_memalign(&buf, 4096, REC)) {      /* O_DIRECT хоче вирівняний буфер */
        fprintf(stderr, "posix_memalign не дав пам'яті\n");
        return 1;
    }
    memset(buf, 0xA5, REC);

    int fd = open(argv[1], O_WRONLY | O_CREAT | O_DIRECT, 0600);
    if (fd < 0) { perror(argv[1]); return 1; }
    if (fallocate(fd, 0, 0, (off_t)(SPAN + REC)))
        perror("fallocate (для блокового пристрою — очікувано)");

    one_pass(fd, buf, 0, 1);                    /* вхолосту: розмітити ділянки */
    fsync(fd);

    put_label("прохід");
    puts(" запитів    злитих       МіБ  запит,КіБ    секунд");
    measure("вирівняно, суцільно", fd, buf, argv[2],   0, 1);
    measure("зсув 512, суцільно",  fd, buf, argv[2], 512, 1);
    measure("вирівняно, вроздріб", fd, buf, argv[2],   0, SKIP);
    measure("зсув 512, вроздріб",  fd, buf, argv[2], 512, SKIP);

    close(fd);
    free(buf);
    return 0;
}
