struct super_operations {
    struct inode *(*alloc_inode)(struct super_block *sb);
    void (*destroy_inode)(struct inode *);
    void (*free_inode)(struct inode *);
    void (*dirty_inode)(struct inode *, int flags);
    int  (*write_inode)(struct inode *, struct writeback_control *wbc);
    int  (*drop_inode)(struct inode *);
    void (*evict_inode)(struct inode *);
    void (*put_super)(struct super_block *);
    int  (*sync_fs)(struct super_block *sb, int wait);
    int  (*freeze_fs)(struct super_block *);
    int  (*unfreeze_fs)(struct super_block *);
    int  (*statfs)(struct dentry *, struct kstatfs *);
    void (*umount_begin)(struct super_block *);
    int  (*show_options)(struct seq_file *, struct dentry *);
    long (*nr_cached_objects)(struct super_block *, struct shrink_control *);
    long (*free_cached_objects)(struct super_block *, struct shrink_control *);
};
