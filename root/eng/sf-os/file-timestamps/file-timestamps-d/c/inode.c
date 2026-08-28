/* Ядро Linux: fs/inode.c — перевірка необхідності оновлення atime у режимі relatime */
static int relatime_need_update(struct vfsmount *mnt, struct inode *inode,
                                struct timespec64 now)
{
    /* Якщо atime старіший за mtime — оновити */
    if (timespec64_compare(&inode->i_atime, &inode->i_mtime) <= 0)
        return 1;
    /* Якщо atime старіший за ctime — оновити */
    if (timespec64_compare(&inode->i_atime, &inode->i_ctime) <= 0)
        return 1;
    /* Якщо минуло більше 24 годин — оновити */
    if ((now.tv_sec - inode->i_atime.tv_sec) >= 24 * 60 * 60)
        return 1;

    return 0;
}
