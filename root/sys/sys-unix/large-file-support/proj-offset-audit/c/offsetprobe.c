/* offsetprobe.c — що означає off_t у цій збірці й де стоїть стеля.
 *
 *   cc -m32                        offsetprobe.c -o probe-narrow
 *   cc -m32 -D_FILE_OFFSET_BITS=64 offsetprobe.c -o probe-wide
 *
 * _GNU_SOURCE тут лише щоб побачити константу O_LARGEFILE: у glibc вона
 * схована за _LARGEFILE64_SOURCE. На ширину off_t _GNU_SOURCE НЕ впливає.
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stddef.h>
#include <stdint.h>
#include <limits.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <sys/types.h>

#define SIGNED_MAX(T) \
    ((T)(((((uintmax_t)1 << (sizeof(T) * CHAR_BIT - 2)) - 1) * 2) + 1))

static void report_build(void)
{
    printf("ширина типів у цій збірці\n");
    printf("  sizeof(off_t)          = %zu\n", sizeof(off_t));
    printf("  sizeof(struct stat)    = %zu\n", sizeof(struct stat));
    printf("  offsetof(stat,st_size) = %zu\n", offsetof(struct stat, st_size));
    printf("  найбільший зсув        = %jd\n", (intmax_t)SIGNED_MAX(off_t));
#ifdef _FILE_OFFSET_BITS
    printf("  _FILE_OFFSET_BITS      = %d\n", _FILE_OFFSET_BITS);
#else
    printf("  _FILE_OFFSET_BITS      не визначено\n");
#endif
    printf("  O_LARGEFILE            = %d\n", O_LARGEFILE);
}

static void probe_file(const char *path)
{
    printf("\nфайл: %s\n", path);

    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        printf("  open → %s (errno=%d)\n", strerror(errno), errno);
        if (errno == EOVERFLOW)
            printf("  ← відмовило ЯДРО: розмір не вміщається в st_size цієї збірки\n");
        return;
    }
    printf("  open → успіх, fd=%d\n", fd);

    struct stat st;
    if (fstat(fd, &st) == 0) {
        printf("  st_size          = %jd\n", (intmax_t)st.st_size);
        printf("  st_blocks · 512  = %jd (справді зайнято на носії)\n",
               (intmax_t)st.st_blocks * 512);
    } else {
        printf("  fstat → %s\n", strerror(errno));
    }

    /* Ціль — перший байт за межею 2³¹. Рахуємо в intmax_t, щоб перевірити,
       чи взагалі можна назвати цю ціль типом off_t — ДО системного виклику. */
    intmax_t want = INTMAX_C(1) << 31;
    if (want > (intmax_t)SIGNED_MAX(off_t)) {
        printf("  lseek(%jd) навіть не буде викликано\n", want);
        printf("  ← стеля в САМІЙ ПРОГРАМІ: такого числа off_t не тримає\n");
    } else {
        off_t got = lseek(fd, (off_t)want, SEEK_SET);
        if (got == (off_t)-1)
            printf("  lseek(%jd) → -1, %s\n", want, strerror(errno));
        else
            printf("  lseek(%jd) → %jd\n", want, (intmax_t)got);
    }
    close(fd);
}

int main(int argc, char **argv)
{
    report_build();
    for (int i = 1; i < argc; i++)
        probe_file(argv[i]);
    return 0;
}
