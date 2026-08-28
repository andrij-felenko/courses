#include <sys/syscall.h>
#include <unistd.h>
#include <system_error>

#ifndef __NR_statx
# error "Архітектура ядра не визначає системний виклик __NR_statx"
#endif

inline int my_statx(int dirfd, const char *path, int flags,
                     unsigned int mask, struct statx *stx) noexcept {
    return static_cast<int>(::syscall(__NR_statx, dirfd, path, flags, mask, stx));
}
