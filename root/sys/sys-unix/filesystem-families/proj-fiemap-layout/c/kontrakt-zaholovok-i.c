/* Цитата з <linux/fiemap.h> */
struct fiemap {
    __u64 fm_start;             /* з якого зсуву питаємо        — вхід  */
    __u64 fm_length;            /* яку довжину хочемо покрити   — вхід  */
    __u32 fm_flags;             /* FIEMAP_FLAG_*            — вхід/вихід */
    __u32 fm_mapped_extents;    /* скільки записів заповнено    — вихід */
    __u32 fm_extent_count;      /* скільки слотів ми дали       — вхід  */
    __u32 fm_reserved;
    struct fiemap_extent fm_extents[];
};
