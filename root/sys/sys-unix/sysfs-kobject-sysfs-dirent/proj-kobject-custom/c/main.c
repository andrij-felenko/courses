#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/kobject.h>
#include <linux/string.h>
#include <linux/sysfs.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix Reference Course");
MODULE_DESCRIPTION("Demo Kernel Module for kobject and sysfs attributes");
MODULE_VERSION("1.0");

static struct kobject *demo_kobj;
static int counter = 42;
static char control_buffer[64] = "default_state";

/* Обробник читання атрибута status */
static ssize_t status_show(struct kobject *kobj, struct kobj_attribute *attr,
                           char *buf)
{
    return sysfs_emit(buf, "%d\n", counter++);
}

/* Обробник читання атрибута control */
static ssize_t control_show(struct kobject *kobj, struct kobj_attribute *attr,
                            char *buf)
{
    return sysfs_emit(buf, "%s\n", control_buffer);
}

/* Обробник запису атрибута control */
static ssize_t control_store(struct kobject *kobj, struct kobj_attribute *attr,
                             const char *buf, size_t count)
{
    if (count >= sizeof(control_buffer))
        return -EINVAL;

    sscanf(buf, "%63s", control_buffer);
    pr_info("demo_kobj: control state updated to '%s'\n", control_buffer);

    return count;
}

/* Оголошення об'єктів атрибутів через макроси */
static struct kobj_attribute status_attr = __ATTR_RO(status);
static struct kobj_attribute control_attr = __ATTR_RW(control);

/* Масив атрибутів для формування групи */
static struct attribute *demo_attrs[] = {
    &status_attr.attr,
    &control_attr.attr,
    NULL, /* Термінатор масиву */
};

static struct attribute_group demo_attr_group = {
    .attrs = demo_attrs,
};

static int __init demo_init(void)
{
    int retval;

    /* Створення kobject під /sys/kernel/ */
    demo_kobj = kobject_create_and_add("demo_kobj", kernel_kobj);
    if (!demo_kobj)
        return -ENOMEM;

    /* Реєстрація групи атрибутів у sysfs */
    retval = sysfs_create_group(demo_kobj, &demo_attr_group);
    if (retval) {
        kobject_put(demo_kobj);
        return retval;
    }

    pr_info("demo_kobj: module loaded, /sys/kernel/demo_kobj created\n");
    return 0;
}

static void __exit demo_exit(void)
{
    /* Спершу видаляємо атрибути, потім зменшуємо kref */
    sysfs_remove_group(demo_kobj, &demo_attr_group);
    kobject_put(demo_kobj);
    pr_info("demo_kobj: module unloaded\n");
}

module_init(demo_init);
module_exit(demo_exit);
