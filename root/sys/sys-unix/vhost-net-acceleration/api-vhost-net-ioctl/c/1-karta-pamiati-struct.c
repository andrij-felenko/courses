struct vhost_memory_region {
    uint64_t guest_phys_addr; /* Початкова фізична адреса у гості (GPA) */
    uint64_t memory_size;     /* Розмір сегмента пам'яті в байтах */
    uint64_t userspace_addr;  /* Початкова віртуальна адреса в гіпервізорі (HVA) */
    uint64_t flags_padding;   /* Допоміжні прапори та вирівнювання */
};

struct vhost_memory {
    uint32_t nregions;        /* Кількість сегментів пам'яті */
    uint32_t padding;         /* Вирівнювання структури */
    struct vhost_memory_region regions[0]; /* Гнучкий масив сегментів */
};
