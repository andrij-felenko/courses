#define _GNU_SOURCE
#include <linux/openat2.h>    /* struct open_how, RESOLVE_* */
#include <sys/syscall.h>
#include <unistd.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>

#ifndef __NR_openat2
#define __NR_openat2 437      /* номер на x86-64, arm64 та решті поширених */
#endif

/* Відкрити шлях, отриманий іззовні, не випустивши обхід за межі root. */
int open_in_root(int root, const char *user_path)
{
    struct open_how how;
    memset(&how, 0, sizeof how);          /* нулі обов'язкові */
    how.flags   = O_RDONLY | O_CLOEXEC;
    how.resolve = RESOLVE_IN_ROOT | RESOLVE_NO_MAGICLINKS;

    int fd;
    do {
        fd = (int)syscall(__NR_openat2, root, user_path,
                          &how, sizeof how);
    } while (fd < 0 && errno == EAGAIN);   /* EAGAIN тут тимчасовий */
    return fd;
}
