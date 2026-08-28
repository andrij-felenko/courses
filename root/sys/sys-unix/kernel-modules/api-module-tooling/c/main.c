#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>

#ifndef MODULE_INIT_COMPRESSED_FILE
#define MODULE_INIT_COMPRESSED_FILE 4
#endif

static int finit_module(int fd, const char *params, int flags)
{
    return syscall(SYS_finit_module, fd, params, flags);
}

static int delete_module(const char *name, unsigned int flags)
{
    return syscall(SYS_delete_module, name, flags);
}

/* стиснений .ko розпакує саме ядро — інакше довелося б робити це тут */
static int compressed(const char *path)
{
    const char *dot = strrchr(path, '.');
    return dot && (strcmp(dot, ".zst") == 0 ||
                   strcmp(dot, ".xz")  == 0 ||
                   strcmp(dot, ".gz")  == 0);
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "вжиток: %s load ФАЙЛ.ko [\"параметри\"] | %s unload НАЗВА\n",
                argv[0], argv[0]);
        return 2;
    }

    if (strcmp(argv[1], "load") == 0) {
        int fd = open(argv[2], O_RDONLY | O_CLOEXEC);
        if (fd < 0) { perror("open"); return 1; }

        int flags = compressed(argv[2]) ? MODULE_INIT_COMPRESSED_FILE : 0;

        if (finit_module(fd, argc > 3 ? argv[3] : "", flags) != 0) {
            fprintf(stderr, "finit_module: %s (errno %d) — подробиці в dmesg\n",
                    strerror(errno), errno);
            close(fd);
            return 1;
        }
        close(fd);            /* образ уже в ядрі, дескриптор більше ні до чого */
        puts("завантажено");
        return 0;
    }

    if (delete_module(argv[2], O_NONBLOCK) != 0) {
        fprintf(stderr, "delete_module: %s (errno %d)\n", strerror(errno), errno);
        return 1;
    }
    puts("вивантажено");
    return 0;
}
