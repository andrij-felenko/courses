/* Спрощена концептуальна схема захисту у debugfs */
ssize_t debugfs_file_read(struct file *file, char __user *buf, 
                          size_t val, loff_t *ppos)
{
    struct dentry *dentry = file->f_path.dentry;
    int idx;
    ssize_t ret;

    /* 1. Захоплюємо SRCU read lock для перевірки життєздатності dentry */
    if (debugfs_file_get(dentry, &idx))
        return -EIO; /* Файл вже видаляється модулем! */

    /* 2. Безпечно викликаємо реальний fops драйвера */
    ret = real_fops->read(file, buf, val, ppos);

    /* 3. Звільняємо SRCU read lock */
    debugfs_file_put(dentry, idx);

    return ret;
}
