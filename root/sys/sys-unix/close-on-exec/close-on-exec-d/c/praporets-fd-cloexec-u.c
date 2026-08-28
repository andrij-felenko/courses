/* Структури ядра Linux (простір ядра) */
struct files_struct {
    atomic_t count;
    struct fdtable __rcu *fdt;
    struct fdtable fdtab;
    spinlock_t file_lock;
    /* ... */
};

struct fdtable {
    unsigned int max_fds;
    struct file __rcu **fd;      /* Масив вказівників на структури struct file */
    unsigned long *close_on_exec; /* Бітова маска прапорців FD_CLOEXEC */
    unsigned long *open_fds;      /* Бітова маска зайнятих індексів fd */
    struct rcu_head rcu;
};
