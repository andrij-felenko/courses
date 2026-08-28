// Спрощений фрагмент ініціалізації спеціального інода у ядрі Linux (fs/inode.c)
void init_special_inode(struct inode *inode, umode_t mode, dev_t rdev) {
    inode->i_mode = mode;
    if (S_ISCHR(mode)) {
        inode->i_fop = &def_chr_fops;   // єдиний робочий метод — chrdev_open()
        inode->i_rdev = rdev;
    } else if (S_ISBLK(mode)) {
        inode->i_fop = &def_blk_fops;   // вхід у блочний шар
        inode->i_rdev = rdev;
    }
}
