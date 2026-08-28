#include <sys/syscall.h>

#ifndef __NR_statx
# error "Архітектура ядра не визначає системний виклик __NR_statx"
#endif

static inline int my_statx(int dirfd, const char *path, int flags,
                           unsigned int mask, struct statx *stx) {
    return syscall(__NR_statx, dirfd, path, flags, mask, stx);
}
