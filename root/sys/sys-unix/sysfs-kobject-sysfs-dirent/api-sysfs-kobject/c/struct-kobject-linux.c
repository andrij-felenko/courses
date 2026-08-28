struct kobject {
    const char          *name;        /* Ім'я вузла у sysfs */
    struct list_head    entry;       /* Елемент списку в kset */
    struct kobject      *parent;     /* Вказівник на батьківський kobject */
    struct kset         *kset;       /* Вказівник на набір-власник */
    const struct kobj_type *ktype;   /* Таблиця операцій та тип об'єкта */
    struct kernfs_node  *sd;          /* Легковаговий вузол у kernfs/sysfs */
    struct kref         kref;        /* Лічильник посилань */
    unsigned int state_initialized:1;
    unsigned int state_in_sysfs:1;
    unsigned int state_add_uevent_sent:1;
    unsigned int state_remove_uevent_sent:1;
    unsigned int uevent_suppress:1;
};
