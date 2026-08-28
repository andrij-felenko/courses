struct kernfs_syscall_ops {
    int (*remount_fs)(struct kernfs_root *root, int *flags, char *data);
    int (*show_options)(struct seq_file *sf, struct kernfs_root *root);
    int (*mkdir)(struct kernfs_node *parent, const char *name, umode_t mode);
    int (*rmdir)(struct kernfs_node *kn);
    int (*rename)(struct kernfs_node *kn, struct kernfs_node *new_parent,
                  const char *new_name);
    int (*show_path)(struct seq_file *sf, struct kernfs_node *kn,
                     struct kernfs_root *root);
};
