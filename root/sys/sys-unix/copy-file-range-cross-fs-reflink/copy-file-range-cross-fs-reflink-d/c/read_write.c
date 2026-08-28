// Спрощений алгоритм маршрутизації у ядрі Linux (fs/read_write.c)
ssize_t vfs_copy_file_range(struct file *file_in, loff_t pos_in,
                            struct file *file_out, loff_t pos_out,
                            size_t len, unsigned int flags)
{
    // 1. Перевірка прапорців та прав доступу VFS
    if (flags != 0) return -EINVAL;
    if (!(file_in->f_mode & FMODE_READ) || !(file_out->f_mode & FMODE_WRITE))
        return -EBADF;

    // 2. Спроба виконання Reflink (якщо ФС підтримує CoW і sb_in == sb_out)
    if (file_inode(file_in)->i_sb == file_inode(file_out)->i_sb) {
        if (file_out->f_op->remap_file_range) {
            loff_t remap_len = file_out->f_op->remap_file_range(
                file_in, pos_in, file_out, pos_out, len, REMAP_FILE_CAN_SHORTEN);
            if (remap_len > 0) return remap_len;
        }
    }

    // 3. Спроба виклику драйвера файлової системи (NFS SSC, SMB3 CopyChunk)
    if (file_out->f_op->copy_file_range) {
        ssize_t ret = file_out->f_op->copy_file_range(
            file_in, pos_in, file_out, pos_out, len, flags);
        if (ret != -EOPNOTSUPP && ret != -EXDEV) return ret;
    }

    // 4. Універсальний VFS-фолбек через Kernel Page Cache та splice
    return generic_copy_file_range(file_in, pos_in, file_out, pos_out, len, flags);
}
