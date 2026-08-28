struct attribute {
    const char *name;
    umode_t mode;
};

struct bin_attribute {
    struct attribute attr;
    size_t size;
    void *private;
    struct address_space *(*f_mapping)(void);
    ssize_t (*read)(struct file *, struct kobject *, struct bin_attribute *, char *, loff_t, size_t);
    ssize_t (*write)(struct file *, struct kobject *, struct bin_attribute *, char *, loff_t, size_t);
    int (*mmap)(struct file *, struct kobject *, struct bin_attribute *attr, struct vm_area_struct *vma);
};
