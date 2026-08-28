struct dentry_operations {
    int  (*d_revalidate)(struct inode *, const struct qstr *, struct dentry *, unsigned int);
    int  (*d_weak_revalidate)(struct dentry *, unsigned int);
    int  (*d_hash)(const struct dentry *, struct qstr *);
    int  (*d_compare)(const struct dentry *, unsigned int, const char *, const struct qstr *);
    int  (*d_delete)(const struct dentry *);
    void (*d_release)(struct dentry *);
    void (*d_iput)(struct dentry *, struct inode *);
    char *(*d_dname)(struct dentry *, char *, int);
    struct vfsmount *(*d_automount)(struct path *);
    int  (*d_manage)(const struct path *, bool);
};
