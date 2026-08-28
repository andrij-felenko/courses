struct fanout_slot {
    struct cdev  cdev;       /* свій запис у мапі на кожен примірник */
    struct mutex lock;
    char   buf[FANOUT_SIZE];
    size_t len;
};

/* в init, для кожного i: */
cdev_init(&slots[i].cdev, &fanout_fops);
slots[i].cdev.owner = THIS_MODULE;
cdev_add(&slots[i].cdev, MKDEV(MAJOR(first), i), 1);

/* і тоді в open молодший номер узагалі не потрібен: */
static int fanout_open(struct inode *inode, struct file *file)
{
    file->private_data = container_of(inode->i_cdev, struct fanout_slot, cdev);
    return 0;
}
