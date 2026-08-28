/* kernel/include/linux/fdtable.h */
struct fdtable {
    unsigned int max_fds;
    struct file **fd;      /* Масив вказівників на відкриті файли ядра */
    unsigned long *close_on_exec;
    unsigned long *open_fds;
    struct rcu_head rcu;
};

struct files_struct {
    atomic_t count;
    bool resize_in_progress;
    wait_queue_head_t resize_wait;
    struct fdtable __rcu *fdt;
    struct fdtable fdtab;
    /* Початковий статичний масив для швидкого доступу без динамічної пам'яті */
    struct file * fd_array[NR_OPEN_DEFAULT];
};

/* kernel/include/linux/fs.h */
struct file {
    union {
        struct llist_node   fu_llist;
        struct rcu_head     fu_rcuhead;
    } f_u;
    struct path             f_path;
    struct inode           *f_inode;     /* Вказівник на іноду VFS */
    const struct file_operations *f_op;  /* Таблиця системних операцій файлу */
    spinlock_t              f_lock;
    atomic_long_t           f_count;     /* Лічильник посилань на відкритий файл */
    unsigned int            f_flags;     /* Прапорці відкриття (O_RDWR, O_APPEND...) */
    fmode_t                 f_mode;
    loff_t                  f_pos;       /* Поточна позиція зміщення у файлі */
    struct fown_struct      f_owner;
};

struct file_operations {
    struct module *owner;
    loff_t (*llseek) (struct file *, loff_t, int);
    ssize_t (*read) (struct file *, char __user *, size_t, loff_t *);
    ssize_t (*write) (struct file *, const char __user *, size_t, loff_t *);
    __poll_t (*poll) (struct file *, struct poll_table_struct *);
    long (*unlocked_ioctl) (struct file *, unsigned int, unsigned long);
    int (*mmap) (struct file *, struct vm_area_struct *);
    int (*open) (struct inode *, struct file *);
    int (*flush) (struct file *, fl_owner_t id);
    int (*release) (struct inode *, struct file *);
    int (*fsync) (struct file *, loff_t, loff_t, int datasync);
};
