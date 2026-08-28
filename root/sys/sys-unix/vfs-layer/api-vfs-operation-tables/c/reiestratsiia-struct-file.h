struct file_system_type {
    const char *name;            /* ім'я для mount -t і /proc/filesystems */
    int fs_flags;                /* ознаки FS_*, перелік нижче */
    int (*init_fs_context)(struct fs_context *);
    const struct fs_parameter_spec *parameters;
    void (*kill_sb)(struct super_block *);
    struct module *owner;        /* THIS_MODULE */
    struct hlist_node list;      /* внутрішнє: місце в списку зареєстрованих */
    struct hlist_head fs_supers; /* внутрішнє: живі суперблоки цього типу */
    /* далі — ключі класів блокувань для lockdep */
};
