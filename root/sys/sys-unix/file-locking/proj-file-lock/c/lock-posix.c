/* lock-posix.c — POSIX-замок записів; власник — процес плюс файл. */
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>

static int lock_op(int fd, short type, int cmd)
{
    struct flock fl = { .l_type   = type,
                        .l_whence = SEEK_SET,
                        .l_start  = 0,
                        .l_len    = 0 };   /* 0 — до кінця файлу,
                                              хоч би куди той доріс */
    while (fcntl(fd, cmd, &fl) != 0) {
        if (errno != EINTR) return -1;     /* EDEADLK приходить сюди ж —
                                              і повторювати його не можна */
    }
    return 0;
}

int lock_take(int fd) { return lock_op(fd, F_WRLCK, F_SETLKW); }
int lock_drop(int fd) { return lock_op(fd, F_UNLCK, F_SETLK); }
