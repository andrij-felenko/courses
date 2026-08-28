struct dentry {
    unsigned int d_flags;               /* Прапорці стану (DCACHE_*) */
    seqcount_spinlock_t d_seq;          /* Лічильник версій seqlock для RCU-walk */
    struct hlist_bl_node d_hash;        /* Вузол у глобальній dentry_hashtable */
    struct dentry *d_parent;            /* Покажчик на батьківський dentry */
    struct qstr d_name;                 /* Ім'я: hashlen (довжина + хеш) + *name */
    struct inode *d_inode;              /* Покажчик на inode (NULL = негативний dentry) */
    unsigned char d_iname[32];          /* Вбудований буфер коротких імен */

    struct lockref d_lockref;           /* Об'єднані d_lock (spinlock) + d_count */
    const struct dentry_operations *d_op;/* Спеціалізовані операції ФС */
    struct super_block *d_sb;           /* Суперблок файлової системи */
    unsigned long d_time;               /* Часова мітка чинності (для NFS/CIFS) */
    void *d_fsdata;                     /* Приватні дані драйвера ФС */

    union {
        struct list_head d_lru;         /* Вузол у черзі витіснення LRU */
        struct callback_head d_rcu;     /* Захист вивільнення через RCU */
    };
    struct list_head d_subdirs;         /* Голова списку дочірніх dentry */
    struct list_head d_child;           /* Вузол у списку d_subdirs батька */
    struct hlist_node d_alias;          /* Список аліасів одного inode */
} __randomize_layout;
