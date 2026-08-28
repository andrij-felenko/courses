struct ublk_params {
        __u32   len, types;              /* UBLK_PARAM_TYPE_* */
        struct ublk_param_basic    basic;
        struct ublk_param_discard  discard;
        struct ublk_param_devt     devt;     /* ← ядро віддає major/minor обох вузлів */
        struct ublk_param_zoned    zoned;    /* з 6.6 */
        /* далі — dma_align, segment, integrity */
};

struct ublk_param_basic {
        __u32   attrs;                   /* UBLK_ATTR_*            */
        __u8    logical_bs_shift;        /* 9 → 512 Б, 12 → 4 КіБ  */
        __u8    physical_bs_shift;
        __u8    io_opt_shift, io_min_shift;
        __u32   max_sectors;             /* стеля запиту в секторах по 512 Б */
        __u32   chunk_sectors;
        __u64   dev_sectors;             /* розмір пристрою, сектори по 512 Б */
        __u64   virt_boundary_mask;
};
