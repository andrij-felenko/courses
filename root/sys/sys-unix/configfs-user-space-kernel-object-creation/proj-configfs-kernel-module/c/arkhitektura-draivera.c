#include <linux/module.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/configfs.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix-Linux Reference Author");
MODULE_DESCRIPTION("ConfigFS Demo Subsystem Driver");

/* Власна структура об'єкта драйвера */
struct demo_item {
    int                     value;
    bool                    enabled;
    struct config_item      item;
};

/* Макрос безпечного отримання вказівника на структуру драйвера */
static inline struct demo_item *to_demo_item(struct config_item *item)
{
    return item ? container_of(item, struct demo_item, item) : NULL;
}

/* 1. Читання атрибута "value" */
static ssize_t demo_item_value_show(struct config_item *item, char *page)
{
    struct demo_item *demo = to_demo_item(item);
    return sprintf(page, "%d\n", demo->value);
}

/* 2. Запис атрибута "value" */
static ssize_t demo_item_value_store(struct config_item *item, const char *page, size_t count)
{
    struct demo_item *demo = to_demo_item(item);
    int val, ret;

    ret = kstrtoint(page, 10, &val);
    if (ret < 0)
        return ret;

    demo->value = val;
    pr_info("demo_configfs: item '%s' value set to %d\n", config_item_name(item), val);
    return count;
}

/* 3. Читання атрибута "status" */
static ssize_t demo_item_status_show(struct config_item *item, char *page)
{
    struct demo_item *demo = to_demo_item(item);
    return sprintf(page, "enabled=%s, value=%d\n", demo->enabled ? "yes" : "no", demo->value);
}

/* Оголошення атрибутів configfs */
CONFIGFS_ATTR(demo_item_, value);
CONFIGFS_ATTR_RO(demo_item_, status);

static struct configfs_attribute *demo_item_attrs[] = {
    &demo_item_attr_value,
    &demo_item_attr_status,
    NULL,
};

/* 4. Деструктор об'єкта (викликається при ci_kref == 0) */
static void demo_item_release(struct config_item *item)
{
    struct demo_item *demo = to_demo_item(item);
    pr_info("demo_configfs: releasing memory for item '%s'\n", config_item_name(item));
    kfree(demo);
}

static struct configfs_item_operations demo_item_ops = {
    .release = demo_item_release,
};

static const struct config_item_type demo_item_type = {
    .ct_owner    = THIS_MODULE,
    .ct_item_ops = &demo_item_ops,
    .ct_attrs    = demo_item_attrs,
};

/* 5. Метод створення об'єкта при mkdir */
static struct config_item *demo_group_make_item(struct config_group *group, const char *name)
{
    struct demo_item *demo;

    demo = kzalloc(sizeof(*demo), GFP_KERNEL);
    if (!demo)
        return ERR_PTR(-ENOMEM);

    demo->value = 0;
    demo->enabled = true;

    config_item_init_type_name(&demo->item, name, &demo_item_type);
    pr_info("demo_configfs: created item '%s'\n", name);
    return &demo->item;
}

/* 6. Метод вилучення об'єкта при rmdir */
static void demo_group_drop_item(struct config_group *group, struct config_item *item)
{
    struct demo_item *demo = to_demo_item(item);
    pr_info("demo_configfs: dropping item '%s' from group\n", config_item_name(item));
    demo->enabled = false;
    config_item_put(item);
}

static struct configfs_group_operations demo_group_ops = {
    .make_item = demo_group_make_item,
    .drop_item = demo_group_drop_item,
};

static const struct config_item_type demo_group_type = {
    .ct_owner     = THIS_MODULE,
    .ct_group_ops = &demo_group_ops,
};

/* 7. Реєстрація підсистеми верхнього рівня */
static struct configfs_subsystem demo_subsys = {
    .su_group = {
        .cg_item = {
            .ci_namebuf = "demo_target",
            .ci_type    = &demo_group_type,
        },
    },
};

static int __init demo_init(void)
{
    config_group_init(&demo_subsys.su_group);
    mutex_init(&demo_subsys.su_mutex);
    pr_info("demo_configfs: registering subsystem /sys/kernel/config/demo_target/\n");
    return configfs_register_subsystem(&demo_subsys);
}

static void __exit demo_exit(void)
{
    pr_info("demo_configfs: unregistering subsystem\n");
    configfs_unregister_subsystem(&demo_subsys);
}

module_init(demo_init);
module_exit(demo_exit);
