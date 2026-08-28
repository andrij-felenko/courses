static ssize_t kernfs_fop_read(struct file *file, char __user *user_buf,
                               size_t count, loff_t *ppos)
{
    struct kernfs_open_file *of = kernfs_of(file);

    if (of->kn->flags & KERNFS_HAS_SEQ_SHOW)
        return seq_read(file, user_buf, count, ppos);
    else
        return kernfs_file_direct_read(of, user_buf, count, ppos);
}
