#include <linux/mount.h>

struct mount_attr {
    __u64 attr_set;      /* що ввімкнути */
    __u64 attr_clr;      /* що вимкнути  */
    __u64 propagation;   /* MS_SHARED/PRIVATE/SLAVE/UNBINDABLE; 0 — не чіпати */
    __u64 userns_fd;     /* лише для MOUNT_ATTR_IDMAP */
};

int mount_setattr(int dirfd, const char *path, unsigned int flags,
                  struct mount_attr *attr, size_t size);
