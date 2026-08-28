/* lock-flock.c — замок на весь файл; власник — опис відкритого файлу. */
#include <errno.h>
#include <sys/file.h>

int lock_take(int fd)
{
    while (flock(fd, LOCK_EX) != 0)
        if (errno != EINTR) return -1;
    return 0;
}

int lock_drop(int fd) { return flock(fd, LOCK_UN); }
