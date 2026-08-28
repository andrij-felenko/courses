/* crsrun.c — «інтерпретатор», який нічого не інтерпретує, а лише звітує */
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <fcntl.h>
#include <elf.h>

#ifndef AT_FLAGS_PRESERVE_ARGV0            /* include/uapi/linux/binfmts.h */
#define AT_FLAGS_PRESERVE_ARGV0 1
#endif

static void report_file(int fd, const char *whence)
{
    unsigned char head[4];
    char body[256];
    ssize_t n;

    printf("  джерело: %s\n", whence);
    printf("  зсув у файлі: %ld\n", (long) lseek(fd, 0, SEEK_CUR));

    n = read(fd, head, sizeof head);
    if (n != (ssize_t) sizeof head) {
        printf("  прикмету прочитати не вдалося: %s\n", strerror(errno));
        return;
    }
    printf("  прикмета: %02x %02x %02x %02x\n",
           head[0], head[1], head[2], head[3]);

    n = read(fd, body, sizeof body - 1);
    if (n < 0)
        n = 0;
    body[n] = '\0';
    printf("  тіло: %s", body[0] == '\n' ? body + 1 : body);
}

int main(int argc, char **argv, char **envp)
{
    unsigned long *a;
    unsigned long at_flags = 0;
    long execfd = -1;
    const char *execfn = NULL;
    char **p;
    int i, fd;

    printf("argc = %d\n", argc);
    for (i = 0; i < argc; i++)
        printf("argv[%d] = \"%s\"\n", i, argv[i]);

    /* Допоміжний вектор лежить одразу за завершальним NULL масиву envp. */
    for (p = envp; *p; p++)
        ;
    for (a = (unsigned long *) (p + 1); a[0] != AT_NULL; a += 2) {
        switch (a[0]) {
        case AT_FLAGS:  at_flags = a[1];                break;
        case AT_EXECFD: execfd   = (long) a[1];         break;
        case AT_EXECFN: execfn   = (const char *) a[1]; break;
        }
    }

    printf("AT_EXECFN = %s\n", execfn ? execfn : "(немає)");
    printf("AT_FLAGS  = 0x%lx%s\n", at_flags,
           (at_flags & AT_FLAGS_PRESERVE_ARGV0) ? "  ← PRESERVE_ARGV0" : "");

    if (argc < 2) {
        printf("нема чого виконувати\n");
        return 2;
    }

    if (execfd >= 0) {
        printf("AT_EXECFD = %ld\n", execfd);
        fd = (int) execfd;
        printf("  FD_CLOEXEC: %s\n",
               (fcntl(fd, F_GETFD) & FD_CLOEXEC) ? "виставлено"
                                                 : "не виставлено");
        report_file(fd, "готовий дескриптор від ядра");
    } else {
        printf("AT_EXECFD немає — відкриваю за шляхом\n");
        fd = open(argv[1], O_RDONLY);
        if (fd < 0) {
            printf("  open(\"%s\"): %s\n", argv[1], strerror(errno));
            return 1;
        }
        report_file(fd, "власне open() за argv[1]");
    }
    return 0;
}
