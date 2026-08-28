// Перевірка сумісності суперблоків у ядрі Linux (fs/xfs/xfs_reflink.c)
int xfs_reflink_remap_prep(struct file *file_in, loff_t pos_in,
                           struct file *file_out, loff_t pos_out,
                           loff_t *len, unsigned int remap_flags)
{
    struct inode *inode_in = file_inode(file_in);
    struct inode *inode_out = file_inode(file_out);

    // Строга перевірка належності до одного екземпляра super_block
    if (inode_in->i_sb != inode_out->i_sb) {
        return -EXDEV; // Повернення помилки при перетині меж ФС
    }

    // Перевірка прав доступу та режимів блокування
    if (IS_DAX(inode_in) || IS_DAX(inode_out)) {
        return -EOPNOTSUPP;
    }

    return generic_remap_checks(file_in, pos_in, file_out, pos_out, len, remap_flags);
}
