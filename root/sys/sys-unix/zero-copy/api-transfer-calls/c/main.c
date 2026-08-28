#define _GNU_SOURCE
#include <unistd.h>
#include <errno.h>

/* 1 — скопійовано, 0 — виклик недоступний тут, −1 — помилка */
int copy_whole(int in, int out, off_t size)
{
    off_t off_in = 0, off_out = 0;

    while (size > 0) {
        ssize_t n = copy_file_range(in, &off_in, out, &off_out,
                                    (size_t)size, 0);
        if (n > 0) {
            size -= n;               /* зсуви ядро посунуло само */
            continue;
        }
        if (n == 0)
            return -1;               /* файл зрізали під нами */
        if (errno == EINTR)
            continue;
        if (errno == EXDEV || errno == EOPNOTSUPP ||
            errno == ENOSYS || errno == EINVAL)
            return 0;                /* тут не працює — на read/write */
        return -1;
    }
    return 1;
}
