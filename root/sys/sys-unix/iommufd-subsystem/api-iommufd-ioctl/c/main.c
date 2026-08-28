struct iommu_hwpt_alloc {
    __u32 size;
    __u32 flags;
    __u32 dev_id;
    __u32 pt_id;
    __u32 out_hwpt_id;
    __u32 hwpt_type;
    __u32 data_len;
    __aligned_u64 data_uptr;
};
