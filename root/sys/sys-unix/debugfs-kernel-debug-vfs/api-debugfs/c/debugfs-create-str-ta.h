void debugfs_create_str(const char *name, umode_t mode,
                        struct dentry *parent, char **str);

struct debugfs_blob_wrapper {
    void *data;
    unsigned long size;
};

void debugfs_create_blob(const char *name, umode_t mode,
                         struct dentry *parent,
                         struct debugfs_blob_wrapper *blob);
