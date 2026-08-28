struct kernfs_ops {
    int  (*open)(struct kernfs_open_file *of);
    void (*release)(struct kernfs_open_file *of);

    int   (*seq_show)(struct seq_file *sf, void *v);
    void *(*seq_start)(struct seq_file *sf, loff_t *ppos);
    void *(*seq_next)(struct seq_file *sf, void *v, loff_t *ppos);
    void  (*seq_stop)(struct seq_file *sf, void *v);

    ssize_t (*read)(struct kernfs_open_file *of, char *buf,
                    size_t bytes, loff_t off);
    size_t  atomic_write_len;
    bool    prealloc;
    ssize_t (*write)(struct kernfs_open_file *of, char *buf,
                     size_t bytes, loff_t off);

    int (*mmap)(struct kernfs_open_file *of, struct vm_area_struct *vma);
#ifdef CONFIG_DEBUG_LOCK_ALLOC
    struct lock_class_key lockdep_key;
#endif
};
