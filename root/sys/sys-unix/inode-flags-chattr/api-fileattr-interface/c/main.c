struct fsxattr {
        __u32         fsx_xflags;      /* набір FS_XFLAG_* */
        __u32         fsx_extsize;     /* підказка розміру екстента, байти */
        __u32         fsx_nextents;    /* скільки екстентів — лише читання */
        __u32         fsx_projid;      /* проєкт для квот */
        __u32         fsx_cowextsize;  /* підказка розміру для копії-при-записі */
        unsigned char fsx_pad[8];      /* мусить бути нулями */
};

ioctl(fd, FS_IOC_FSGETXATTR, &fa);   /* struct fsxattr * */
ioctl(fd, FS_IOC_FSSETXATTR, &fa);
