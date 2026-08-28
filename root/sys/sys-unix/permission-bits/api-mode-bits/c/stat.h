#include <sys/stat.h>
int chmod(const char *path, mode_t mode);
int fchmod(int fd, mode_t mode);

#include <fcntl.h>          /* AT_* */
#include <sys/stat.h>
int fchmodat(int dirfd, const char *path, mode_t mode, int flags);

#include <sys/syscall.h>    /* обгортки в glibc немає — лише через syscall() */
int syscall(SYS_fchmodat2, int dirfd, const char *path,
            mode_t mode, unsigned int flags);
