/* include/uapi/linux/fs.h */
struct fsxattr {
	__u32  fsx_xflags;      /* сюди й ставиться позначка */
	__u32  fsx_extsize;
	__u32  fsx_nextents;
	__u32  fsx_projid;
	__u32  fsx_cowextsize;
	unsigned char fsx_pad[8];
};

#define FS_XFLAG_DAX        0x00008000
#define FS_IOC_FSGETXATTR   _IOR('X', 31, struct fsxattr)
#define FS_IOC_FSSETXATTR   _IOW('X', 32, struct fsxattr)
