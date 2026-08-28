/* lock-ofd.c — замок на опис відкритого файлу.
   _GNU_SOURCE обов'язковий: без нього F_OFD_SETLKW не оголошено.    */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>

static int lock_op(int fd, short type, int cmd)
{
    struct flock fl = { .l_type   = type,
                        .l_whence = SEEK_SET,
                        .l_start  = 0,
                        .l_len    = 0,
                        .l_pid    = 0 };   /* саме нуль у l_pid і каже ядру,
                                              що заявка на OFD-замок */
    while (fcntl(fd, cmd, &fl) != 0) {
        if (errno != EINTR) return -1;
    }
    return 0;
}

int lock_take(int fd) { return lock_op(fd, F_WRLCK, F_OFD_SETLKW); }
int lock_drop(int fd) { return lock_op(fd, F_UNLCK, F_OFD_SETLK); }
