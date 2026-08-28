#define _GNU_SOURCE
#include <fcntl.h>
#include <sys/stat.h>
#include <unistd.h>
#include <limits.h>

void describe_link(void)
{
    /* Дескриптор на САМЕ посилання, а не на його ціль. */
    int fd = open("/var/log/app", O_PATH | O_NOFOLLOW | O_CLOEXEC);

    struct statx sx;
    statx(fd, "", AT_EMPTY_PATH, STATX_BASIC_STATS, &sx);
    /* S_ISLNK(sx.stx_mode) істинне: це посилання, а не каталог /srv/logs */

    char buf[PATH_MAX];
    ssize_t n = readlinkat(fd, "", buf, sizeof buf - 1);  /* без AT_EMPTY_PATH */
    if (n > 0) buf[n] = '\0';                             /* нуля ядро не додає */

    close(fd);
}
