struct virtio_gpu_mem_entry {
    uint64_t addr;   /* Фізична адреса сторінки в RAM гостя (Guest Physical Address, GPA) */
    uint32_t length; /* Довжина безперервного блоку в байтах */
    uint32_t padding;
};

struct virtio_gpu_resource_attach_backing {
    struct virtio_gpu_ctrl_hdr hdr;
    uint32_t resource_id; /* ID ресурсу, до якого додаються сторінки */
    uint32_t nr_entries;  /* Кількість елементів у масиві mem_entry */
    /* Далі в пам'яті слідує масив struct virtio_gpu_mem_entry entries[nr_entries] */
};
