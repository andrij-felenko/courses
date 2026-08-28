#include <linux/fs.h>

struct fsxattr {
    __u32         fsx_xflags;      /* прапорці FS_XFLAG_* */
    __u32         fsx_extsize;     /* підказка довжини, БАЙТИ */
    __u32         fsx_nextents;    /* лише читання: скільки екстентів зараз */
    __u32         fsx_projid;
    __u32         fsx_cowextsize;  /* те саме для копіювання під час запису */
    unsigned char fsx_pad[8];
};

ioctl(fd, FS_IOC_FSGETXATTR, &fsx);   /* прочитати */
ioctl(fd, FS_IOC_FSSETXATTR, &fsx);   /* записати */
