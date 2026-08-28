/* Заголовок ядра <linux/incrementalfs.h> — Елемент та контейнер заповнення блоків */
#define INCFS_IOC_FILL_BLOCKS _IOW(INCFS_IOCTL_BASE, 2, struct incfs_fill_blocks)

struct incfs_fill_block {
    __u32 block_index;   /* Номер 4KB блоку у файлі (починаючи з 0) */
    __u32 data_len;      /* Розмір даних блоку (зазвичай 4096) */
    __u64 data;          /* Вказівник у користувацькому просторі на буфер даних */
    __u8  compression;   /* 0: Без стиснення, 1: LZ4, 2: ZSTD */
    __u8  flags;         /* Додаткові прапори */
    __u16 reserved;
};

struct incfs_fill_blocks {
    __u64 count;         /* Кількість блоків у масиві fill_blocks */
    __u64 fill_blocks;   /* Вказівник на масив struct incfs_fill_block */
};
