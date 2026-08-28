int single_open(struct file *file,
                int (*show)(struct seq_file *m, void *v),
                void *data);

int single_open_size(struct file *file,
                     int (*show)(struct seq_file *m, void *v),
                     void *data, size_t size);

int single_release(struct inode *inode, struct file *file);

struct proc_dir_entry *proc_create_single(const char *name, umode_t mode,
                                          struct proc_dir_entry *parent,
                                          int (*show)(struct seq_file *, void *));

struct proc_dir_entry *proc_create_single_data(const char *name, umode_t mode,
                                               struct proc_dir_entry *parent,
                                               int (*show)(struct seq_file *, void *),
                                               void *data);
