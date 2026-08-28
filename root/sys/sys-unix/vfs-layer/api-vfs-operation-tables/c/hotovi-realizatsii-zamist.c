const struct inode_operations simple_dir_inode_operations = {
    .lookup = simple_lookup,
};

const struct file_operations simple_dir_operations = {
    .open           = dcache_dir_open,
    .release        = dcache_dir_close,
    .llseek         = dcache_dir_lseek,
    .read           = generic_read_dir,
    .iterate_shared = dcache_readdir,
    .fsync          = noop_fsync,
};
