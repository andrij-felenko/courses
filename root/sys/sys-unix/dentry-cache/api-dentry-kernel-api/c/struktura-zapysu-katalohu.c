struct dentry {
    /* Прапорці стану запису (DCACHE_*) */
    unsigned int d_flags;

    /* Лічильник послідовності seqlock для перевірок в RCU-walk */
    seqcount_spinlock_t d_seq;

    /* Вузол у глобальній хеш-таблиці dentry_hashtable */
    struct hlist_bl_node d_hash;

    /* Вказівник на батьківський каталог */
    struct dentry *d_parent;

    /* Ім'я запису каталогу */
    struct qstr d_name;

    /* Вказівник на пов'язаний inode (NULL для негативних dentry) */
    struct inode *d_inode;

    /* Вбудований буфер для коротких імен (уникає зайвого kmalloc) */
    unsigned char d_iname[DNAME_INLINE_LEN];

    /* Об'єднаний спінлок d_lock та лічильник посилань d_count */
    struct lockref d_lockref;

    /* Таблиця спеціалізованих операцій файлової системи */
    const struct dentry_operations *d_op;

    /* Вказівник на суперблок файлової системи */
    struct super_block *d_sb;

    /* Часова мітка чинності (використовується NFS/CIFS) */
    unsigned long d_time;

    /* Приватні дані файлової системи */
    void *d_fsdata;

    union {
        /* Список витіснення з пам'яті LRU */
        struct list_head d_lru;
        /* Захист відкладеного вивільнення пам'яті через RCU */
        struct callback_head d_rcu;
    };

    /* Список дочірніх dentry поточного каталогу */
    struct list_head d_subdirs;

    /* Вузол у списку d_subdirs батьківського каталогу */
    struct list_head d_child;

    /* Список псевдонімів (жорстких посилань) одного inode */
    struct hlist_node d_alias;
} __randomize_layout;
