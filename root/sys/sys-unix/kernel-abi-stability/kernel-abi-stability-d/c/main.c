#define _GNU_SOURCE
#include <fcntl.h>
#include <linux/openat2.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>

/* Відкрити шлях так, щоб він не вивів за межі каталогу dirfd. */
static int open_beneath(int dirfd, const char *path)
{
    struct open_how how;
    memset(&how, 0, sizeof how);          /* нулі = типова поведінка */
    how.flags   = O_RDONLY | O_CLOEXEC;
    how.resolve = RESOLVE_BENEATH;        /* не виходити за dirfd */

    int fd = syscall(SYS_openat2, dirfd, path, &how, sizeof how);
    if (fd >= 0)
        return fd;

    /* errno == ENOSYS означає «ядро старше за 5.6, openat2 немає»;
       будь-який інший код — справжня помилка відкриття. Розрізняє їх
       той, хто кличе; відкату тут немає навмисно. */
    return -1;
}
