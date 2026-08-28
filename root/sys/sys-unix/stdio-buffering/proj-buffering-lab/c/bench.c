/* bench.c — ціна перетину межі: посимвольний write проти буфера stdio */
#define _POSIX_C_SOURCE 200809L
#include <fcntl.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>

enum { N = 1 << 20, BLK = 4096 };          /* рівно 1 МіБ */

static double now(void)
{
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec * 1e-9;
}

static void row(const char *name, double sec, long calls)
{
    fprintf(stderr, "%s\n    %8.2f мс   %8.1f нс на виклик\n",
            name, sec * 1e3, sec * 1e9 / calls);
}

int main(void)
{
    static char block[BLK];
    double t;

    for (int i = 0; i < BLK; i++) block[i] = 'x';

    int fd = open("/dev/null", O_WRONLY);
    FILE *f = fopen("/dev/null", "w");
    if (fd < 0 || !f) { perror("/dev/null"); return 1; }
    setvbuf(f, NULL, _IOFBF, 0);           /* до першої операції — так можна */

    t = now();
    for (long i = 0; i < N; i++)
        if (write(fd, block, 1) < 0) { perror("write"); return 1; }
    row("А  write по одному байту", now() - t, N);

    t = now();
    for (long i = 0; i < N / BLK; i++)
        if (write(fd, block, BLK) < 0) { perror("write"); return 1; }
    row("Б  write по 4096 байтів", now() - t, N / BLK);

    t = now();
    for (long i = 0; i < N; i++) putc('x', f);
    fflush(f);
    row("В  putc крізь буфер stdio", now() - t, N);

    t = now();
    flockfile(f);
    for (long i = 0; i < N; i++) putc_unlocked('x', f);
    funlockfile(f);
    fflush(f);
    row("Г  putc_unlocked під одним flockfile", now() - t, N);

    t = now();
    for (long i = 0; i < N / BLK; i++)
        if (fwrite(block, 1, BLK, f) != BLK) { perror("fwrite"); return 1; }
    fflush(f);
    row("Д  fwrite блоками по 4096", now() - t, N / BLK);

    fclose(f);
    close(fd);
    return 0;
}
