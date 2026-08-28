static int my_dump_show(struct seq_file *s, void *data)
{
    /* seq_printf автоматично розширює буфер за потреби */
    seq_printf(s, "Driver status: %s\n", "ACTIVE");
    seq_printf(s, "Internal counter: %lu\n", jiffies);
    return 0;
}

static int my_dump_open(struct inode *inode, struct file *file)
{
    return single_open(file, my_dump_show, inode->i_private);
}

static const struct file_operations my_dump_fops = {
    .owner   = THIS_MODULE,
    .open    = my_dump_open,
    .read    = seq_read,
    .llseek  = seq_lseek,
    .release = single_release,
};
