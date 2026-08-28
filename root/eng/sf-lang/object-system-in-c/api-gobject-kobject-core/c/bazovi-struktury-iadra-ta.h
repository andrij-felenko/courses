/* Структури простору ядра Linux */
struct kobject {
    const char          *name;     /* Ім'я об'єкта (каталог у sysfs) */
    struct list_head     entry;    /* Входження до списку kset */
    struct kobject      *parent;   /* Батьківський kobject (ієрархія) */
    struct kset         *kset;     /* Група/підсистема */
    const struct kobj_type *ktype; /* Таблиця операцій та деструктор */
    struct kernfs_node  *sd;       /* Вузол віртуальної ФС sysfs */
    struct kref          kref;     /* Атомарний лічильник посилань */
    unsigned int state_initialized:1;
    unsigned int state_in_sysfs:1;
    unsigned int state_add_uevent_sent:1;
    unsigned int state_remove_uevent_sent:1;
    unsigned int uevent_suppress:1;
};

struct kobj_type {
    void (*release)(struct kobject *kobj);        /* Обов'язковий деструктор */
    const struct sysfs_ops *sysfs_ops;            /* Обробники читання/запису */
    const struct attribute_group **default_groups;/* Файли атрибутів у /sys */
};

struct sysfs_ops {
    ssize_t (*show)(struct kobject *kobj, struct attribute *attr, char *buf);
    ssize_t (*store)(struct kobject *kobj, struct attribute *attr, const char *buf, size_t count);
};
