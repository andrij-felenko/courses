struct vhost_user_memory_region {
    uint64_t guest_phys_addr;   /* Базова адреса регіону в фізичній пам'яті гостя (GPA) */
    uint64_t memory_size;       /* Розмір регіону в байтах */
    uint64_t userspace_addr;    /* Віртуальна адреса регіону в просторі процесу QEMU (QEMU HVA) */
    uint64_t mmap_offset;       /* Зміщення всередині файлу розділюваної пам'яті */
};

struct vhost_user_memory {
    uint32_t nregions;          /* Кількість переданих регіонів */
    uint32_t padding;           /* Вирівнювання структури до 8 байтів */
    struct vhost_user_memory_region regions[8];
};
