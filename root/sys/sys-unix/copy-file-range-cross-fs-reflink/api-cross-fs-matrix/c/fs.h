// Сигнатури функцій у структурі file_operations (include/linux/fs.h)
struct file_operations {
    // Вказівник на специфічну реалізацію copy_file_range у драйвері ФС
    ssize_t (*copy_file_range)(struct file *file_in, loff_t pos_in,
                               struct file *file_out, loff_t pos_out,
                               size_t len, unsigned int flags);

    // Вказівник на реалізацію Reflink / CoW клонування екстентів
    loff_t (*remap_file_range)(struct file *file_in, loff_t pos_in,
                               struct file *file_out, loff_t pos_out,
                               loff_t len, unsigned int remap_flags);

    // Вказівники на потоковий splice
    ssize_t (*splice_read)(struct file *in, loff_t *ppos,
                           struct pipe_inode_info *pipe, size_t len,
                           unsigned int flags);
    ssize_t (*splice_write)(struct pipe_inode_info *pipe, struct file *out,
                            loff_t *ppos, size_t len, unsigned int flags);
};
