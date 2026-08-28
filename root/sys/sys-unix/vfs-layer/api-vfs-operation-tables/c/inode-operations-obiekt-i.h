struct inode_operations {
    struct dentry *(*lookup)(struct inode *, struct dentry *, unsigned int);
    int  (*create)(struct mnt_idmap *, struct inode *, struct dentry *, umode_t, bool);
    int  (*link)(struct dentry *, struct inode *, struct dentry *);
    int  (*unlink)(struct inode *, struct dentry *);
    int  (*symlink)(struct mnt_idmap *, struct inode *, struct dentry *, const char *);
    struct dentry *(*mkdir)(struct mnt_idmap *, struct inode *, struct dentry *, umode_t);
    int  (*rmdir)(struct inode *, struct dentry *);
    int  (*mknod)(struct mnt_idmap *, struct inode *, struct dentry *, umode_t, dev_t);
    int  (*rename)(struct mnt_idmap *, struct inode *, struct dentry *,
                   struct inode *, struct dentry *, unsigned int);
    const char *(*get_link)(struct dentry *, struct inode *, struct delayed_call *);
    int  (*readlink)(struct dentry *, char __user *, int);
    int  (*permission)(struct mnt_idmap *, struct inode *, int);
    int  (*getattr)(struct mnt_idmap *, const struct path *, struct kstat *,
                    u32 request_mask, unsigned int query_flags);
    int  (*setattr)(struct mnt_idmap *, struct dentry *, struct iattr *);
    ssize_t (*listxattr)(struct dentry *, char *, size_t);
    struct posix_acl *(*get_inode_acl)(struct inode *, int, bool);
    int  (*set_acl)(struct mnt_idmap *, struct dentry *, struct posix_acl *, int);
    int  (*fiemap)(struct inode *, struct fiemap_extent_info *, u64 start, u64 len);
    void (*update_time)(struct inode *, enum fs_update_time type, int flags);
    int  (*atomic_open)(struct inode *, struct dentry *, struct file *,
                        unsigned open_flag, umode_t create_mode);
    int  (*tmpfile)(struct mnt_idmap *, struct inode *, struct file *, umode_t);
    int  (*fileattr_get)(struct dentry *, struct file_kattr *);
    int  (*fileattr_set)(struct mnt_idmap *, struct dentry *, struct file_kattr *);
};
