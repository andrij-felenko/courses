#include <sys/ioctl.h>
#include <linux/fs.h>
#include <errno.h>

/* 1 — блоки поділено, 0 — тут так не вміють, -1 — справжня помилка. */
int try_clone(int dest_fd, int src_fd)
{
    if (ioctl(dest_fd, FICLONE, src_fd) == 0)
        return 1;
    if (errno == EOPNOTSUPP || errno == EINVAL || errno == EXDEV)
        return 0;
    return -1;
}
