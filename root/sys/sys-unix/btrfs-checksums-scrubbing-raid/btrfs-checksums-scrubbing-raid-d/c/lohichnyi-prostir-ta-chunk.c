// Запис у Chunk Tree ядра Linux (fs/btrfs/volumes.h)
struct btrfs_chunk {
    u64 length;            // Розмір чанка у байтах (1073741824 = 1 ГіБ)
    u64 owner;             // Ідентифікатор дерева-власника
    u64 stripe_len;        // Розмір страйпа (64 КіБ)
    u64 type;              // Профіль: BTRFS_BLOCK_GROUP_RAID1, RAID5, DUP тощо
    u16 num_stripes;       // Кількість фізичних страйпів (дисків) у цьому чанку
    u16 sub_stripes;
    struct btrfs_stripe stripes[]; // Масив посилань (devid, physical_offset)
} __attribute__ ((packed));
