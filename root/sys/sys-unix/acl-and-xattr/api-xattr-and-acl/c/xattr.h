#include <linux/xattr.h>     /* struct xattr_args */
#include <sys/syscall.h>

struct xattr_args {
    __aligned_u64 value;     /* вказівник на значення */
    __u32 size;              /* довжина значення */
    __u32 flags;             /* XATTR_CREATE / XATTR_REPLACE */
};

/* обгорток у glibc ще немає — кличуть через syscall() */
long syscall(SYS_setxattrat,    int dfd, const char *path, unsigned int at_flags,
                                const char *name, struct xattr_args *args, size_t size);
long syscall(SYS_getxattrat,    int dfd, const char *path, unsigned int at_flags,
                                const char *name, struct xattr_args *args, size_t size);
long syscall(SYS_listxattrat,   int dfd, const char *path, unsigned int at_flags,
                                char *list, size_t size);
long syscall(SYS_removexattrat, int dfd, const char *path, unsigned int at_flags,
                                const char *name);
