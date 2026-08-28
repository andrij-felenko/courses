struct attribute {
    const char *name; /* Ім'я файла в sysfs */
    umode_t     mode; /* Права доступу, наприклад 0644 або 0444 */
};

struct kobj_attribute {
    struct attribute attr;
    ssize_t (*show)(struct kobject *kobj, struct kobj_attribute *attr, char *buf);
    ssize_t (*store)(struct kobject *kobj, struct kobj_attribute *attr, const char *buf, size_t count);
};
