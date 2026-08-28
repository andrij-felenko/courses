#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <unistd.h>

#if __has_include(<linux/openat2.h>)
#  include <linux/openat2.h>
#else                                  /* заголовки старіші за ядро 5.6 */
#  include <linux/types.h>
struct open_how { __u64 flags, mode, resolve; };
#  define RESOLVE_NO_XDEV       0x01
#  define RESOLVE_NO_MAGICLINKS 0x02
#  define RESOLVE_NO_SYMLINKS   0x04
#  define RESOLVE_BENEATH       0x08
#  define RESOLVE_IN_ROOT       0x10
#  define RESOLVE_CACHED        0x20
#endif
#ifndef __NR_openat2
#  define __NR_openat2 437     /* x86, x86-64, ARM, ARM64, RISC-V */
#endif

/* Відкрити path так, ніби root_fd — корінь файлової системи.
   Усе, що з нього виводить, замикається всередині. */
static int open_in_root(int root_fd, const char *path, unsigned long long flags)
{
    struct open_how how = { .flags = flags, .resolve = RESOLVE_IN_ROOT };

    for (int tries = 0; tries < 16; tries++) {
        long fd = syscall(__NR_openat2, root_fd, path, &how, sizeof how);
        if (fd >= 0 || errno != EAGAIN)
            return (int)fd;
        /* EAGAIN: просто під час обходу хтось перейменував каталог або
           щось змонтував, і ядро відмовилося вгадувати. Пробуємо ще. */
    }
    errno = EAGAIN;
    return -1;
}
