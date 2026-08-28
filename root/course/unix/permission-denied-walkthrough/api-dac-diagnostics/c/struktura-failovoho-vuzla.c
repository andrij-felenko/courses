struct inode {
    umode_t         i_mode;         /* Тип файлу (4 біти) + Права доступу (12 бітів) */
    kuid_t          i_uid;          /* Числовий UID власника об'єкта */
    kgid_t          i_gid;          /* Числовий GID групи об'єкта */
    const struct inode_operations *i_op; /* Таблиця методів inode (зокрема i_op->permission) */
    struct super_block *i_sb;       /* Вказівник на суперблок файлової системи */
    unsigned long   i_flags;        /* Системні прапорці файлу (S_IMMUTABLE, S_APPEND тощо) */
    atomic_t        i_count;        /* Лічильник посилань на структуру в пам'яті */
    unsigned int    i_nlink;        /* Кількість жорстких посилань на диску */
};
