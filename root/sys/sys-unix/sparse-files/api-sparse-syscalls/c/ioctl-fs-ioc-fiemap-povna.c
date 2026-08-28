#include <linux/fiemap.h>
#include <linux/fs.h>    /* FS_IOC_FIEMAP _IOWR('f', 11, struct fiemap) */

struct fiemap_extent {
    __u64 fe_logical;    /* зсув у файлі, байти */
    __u64 fe_physical;   /* зсув на носії, байти */
    __u64 fe_length;     /* довжина, байти */
    __u64 fe_reserved64[2];
    __u32 fe_flags;
    __u32 fe_reserved[3];
};

struct fiemap {
    __u64 fm_start;              /* від якого зсуву питаємо */
    __u64 fm_length;             /* яку довжину покрити; FIEMAP_MAX_OFFSET = ~0ULL */
    __u32 fm_flags;              /* вхід: прапорці запиту */
    __u32 fm_mapped_extents;     /* вихід: скільки екстентів заповнено */
    __u32 fm_extent_count;       /* вхід: скільки місця у буфері */
    __u32 fm_reserved;
    struct fiemap_extent fm_extents[];
};
