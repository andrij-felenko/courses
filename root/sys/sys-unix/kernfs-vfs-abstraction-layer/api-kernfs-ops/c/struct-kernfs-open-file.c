struct kernfs_open_file {
    struct kernfs_node  *kn;
    struct file         *file;
    struct seq_file     *seq_file;
    void                *priv;

    struct mutex        mutex;
    struct mutex        prealloc_mutex;
    int                 event;
    struct list_head    list;
    char                *prealloc_buf;

    size_t              atomic_write_len;
    bool                mmapped:1;
    bool                released:1;
    const struct vm_operations_struct *vm_ops;
};
