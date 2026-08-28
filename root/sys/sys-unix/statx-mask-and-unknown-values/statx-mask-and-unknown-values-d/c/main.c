#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/stat.h>

/* 1 — час створення відомий і покладений у *sec; 0 — невідомий; -1 — помилка. */
int file_birth_time(int dirfd, const char *path, long long *sec)
{
    struct statx sx;

    if (statx(dirfd, path, AT_SYMLINK_NOFOLLOW, STATX_BTIME, &sx) != 0)
        return -1;                       /* файлу немає, немає прав, обірвався сервер */

    if (!(sx.stx_mask & STATX_BTIME))
        return 0;                        /* виклик удався, але часу створення немає */

    *sec = sx.stx_btime.tv_sec;
    return 1;
}
