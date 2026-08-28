struct kernfs_node *kernfs_create_file_ns(
    struct kernfs_node *parent,
    const char *name,
    umode_t mode,
    kuid_t uid, kgid_t gid,
    loff_t size,
    const struct kernfs_ops *ops,
    void *priv,
    const void *ns
);
