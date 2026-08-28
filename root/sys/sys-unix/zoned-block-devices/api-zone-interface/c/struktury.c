struct blk_zone_range {
        __u64 sector;         /* початок діапазону, 512-Б сектори */
        __u64 nr_sectors;     /* довжина діапазону */
};

struct blk_zone_report {
        __u64 sector;         /* вхід: звідки почати обхід */
        __u32 nr_zones;       /* вхід: скільки описів уміщає буфер,
                                 вихід: скільки ядро туди поклало */
        __u32 flags;          /* вихід: BLK_ZONE_REP_CAPACITY (з 5.9) */
        struct blk_zone zones[];
};

struct blk_zone {
        __u64 start;          /* перший сектор зони */
        __u64 len;            /* розмір зони, степінь двійки */
        __u64 wp;             /* вказівник запису */
        __u8  type;           /* enum blk_zone_type */
        __u8  cond;           /* enum blk_zone_cond */
        __u8  non_seq;        /* у зоні є непослідовно записане */
        __u8  reset;          /* пристрій радить скинути зону */
        __u8  resv[4];
        __u64 capacity;       /* придатне до запису, з 5.9 */
        __u8  reserved[24];
};
