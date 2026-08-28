#define _GNU_SOURCE
#include <sys/random.h>
#include <sys/stat.h>
#include <sys/sysmacros.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <stdint.h>

static int urandom_fd = -1;

/* Викликати РІВНО один раз, найпершою дією в main() — до chroot,
   до зниження прав, до створення потоків. 0 — запасний шлях готовий. */
int random_init(void)
{
    int fd = open("/dev/urandom", O_RDONLY | O_CLOEXEC | O_NOCTTY);
    if (fd < 0)
        return -1;

    struct stat st;
    if (fstat(fd, &st) < 0) {
        close(fd);
        return -1;
    }

    /* Мусить бути символьний пристрій 1:9, а не підкладений файл. */
    if (!S_ISCHR(st.st_mode) ||
        major(st.st_rdev) != 1 || minor(st.st_rdev) != 9) {
        close(fd);
        errno = ENODEV;
        return -1;
    }

    urandom_fd = fd;
    return 0;
}
