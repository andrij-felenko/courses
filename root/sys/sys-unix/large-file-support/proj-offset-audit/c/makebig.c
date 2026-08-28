/* makebig.c — дешевий великий файл: діра плюс один справжній байт наприкінці.
   cc -m32 $(getconf LFS_CFLAGS) makebig.c -o makebig */
#define _FILE_OFFSET_BITS 64   /* ЛИШЕ для самодостатності прикладу; у справжньому
                                  проєкті цей макрос належить прапорцям збирання */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>
#include <fcntl.h>
#include <unistd.h>

#define SIGNED_MAX(T) \
    ((T)(((((uintmax_t)1 << (sizeof(T) * CHAR_BIT - 2)) - 1) * 2) + 1))

int main(int argc, char **argv)
{
    if (argc != 3) { fprintf(stderr, "makebig <файл> <ГіБ>\n"); return 2; }

    long gib = strtol(argv[2], NULL, 10);
    if (gib <= 0 || gib > (long)(SIGNED_MAX(off_t) >> 30)) {
        fprintf(stderr, "%ld ГіБ не назвати типом off_t завширшки %zu байтів\n",
                gib, sizeof(off_t));
        return 2;
    }
    off_t size = (off_t)gib << 30;

    int fd = open(argv[1], O_RDWR | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) { perror("open"); return 1; }
    if (ftruncate(fd, size) < 0) { perror("ftruncate"); return 1; }
    if (pwrite(fd, "!", 1, size - 1) != 1) { perror("pwrite"); return 1; }
    close(fd);

    printf("створено %s: %jd байтів\n", argv[1], (intmax_t)size);
    return 0;
}
