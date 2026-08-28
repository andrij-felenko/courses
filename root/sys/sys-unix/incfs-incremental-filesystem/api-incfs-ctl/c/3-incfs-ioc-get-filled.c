/* Заголовок ядра <linux/incrementalfs.h> — Запит діапазонів заповнених блоків */
#define INCFS_IOC_GET_FILLED_BLOCKS _IOWR(INCFS_IOCTL_BASE, 3, struct incfs_get_filled_blocks_args)

struct incfs_filled_range {
    __u32 start_block_index;  /* Початковий блок діапазону */
    __u32 end_block_index;    /* Кінцевий блок діапазону (включно) */
};

struct incfs_get_filled_blocks_args {
    __u64 range_buffer;          /* Вказівник на масив struct incfs_filled_range */
    __u32 range_buffer_size;     /* Розмір виділеного буфера у байтах */
    __u32 start_index;           /* З якого блоку починати перегляд */
    __u32 end_index;             /* На якому блоці зупинитися */
    __u32 total_blocks_out;      /* Скільки всього блоків у файлі */
    __u32 range_buffer_size_out; /* Скільки байтів записано в буфер */
    __u32 index_out;             /* Блок, на якому перегляд зупинився */
};
