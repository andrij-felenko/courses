// sample_kobject_module.c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/kobject.h>
#include <linux/slab.h>
#include <linux/sysfs.h>
#include <linux/string.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Kernel Architecture Guide");
MODULE_DESCRIPTION("Dynamic kobject embedding and lifetime management example");

/* Власна структура драйвера, що інкапсулює апаратний або логічний контекст */
struct sample_device {
    int dev_id;
    int baud_rate;
    char status_str[32];
    struct kobject kobj; /* Вбудований atomic kobject */
};

/* Специфічний атрибут для нашого типу пристрою */
struct sample_attribute {
    struct attribute attr;
    ssize_t (*show)(struct sample_device *dev, struct sample_attribute *attr, char *buf);
    ssize_t (*store)(struct sample_device *dev, struct sample_attribute *attr, const char *buf, size_t count);
};

#define to_sample_attr(a) container_of(a, struct sample_attribute, attr)

/* ── Зворотний виклик звільнення пам'яті (Деструктор) ────────────────────── */
static void sample_device_release(struct kobject *kobj)
{
    struct sample_device *dev = container_of(kobj, struct sample_device, kobj);
    pr_info("sample_device: release callback executed for dev_id=%d. Freeing memory at %p\n",
            dev->dev_id, dev);
    kfree(dev);
}

/* ── Диспетчеризація операцій sysfs ─────────────────────────────────────── */
static ssize_t sample_attr_show(struct kobject *kobj, struct attribute *attr, char *buf)
{
    struct sample_device *dev = container_of(kobj, struct sample_device, kobj);
    struct sample_attribute *sattr = to_sample_attr(attr);

    if (!sattr->show)
        return -EIO;
    return sattr->show(dev, sattr, buf);
}

static ssize_t sample_attr_store(struct kobject *kobj, struct attribute *attr, const char *buf, size_t count)
{
    struct sample_device *dev = container_of(kobj, struct sample_device, kobj);
    struct sample_attribute *sattr = to_sample_attr(attr);

    if (!sattr->store)
        return -EIO;
    return sattr->store(dev, sattr, buf, count);
}

static const struct sysfs_ops sample_sysfs_ops = {
    .show  = sample_attr_show,
    .store = sample_attr_store,
};

/* ── Обробники окремих атрибутів ────────────────────────────────────────── */
static ssize_t baud_rate_show(struct sample_device *dev, struct sample_attribute *attr, char *buf)
{
    return sysfs_emit(buf, "%d\n", dev->baud_rate);
}

static ssize_t baud_rate_store(struct sample_device *dev, struct sample_attribute *attr, const char *buf, size_t count)
{
    int val, ret;
    ret = kstrtoint(buf, 10, &val);
    if (ret < 0)
        return ret;
    if (val <= 0 || val > 3000000)
        return -EINVAL;
    dev->baud_rate = val;
    return count;
}

static ssize_t status_show(struct sample_device *dev, struct sample_attribute *attr, char *buf)
{
    return sysfs_emit(buf, "%s\n", dev->status_str);
}

static struct sample_attribute attr_baud = {
    .attr = { .name = "baud_rate", .mode = 0644 },
    .show = baud_rate_show,
    .store = baud_rate_store,
};

static struct sample_attribute attr_status = {
    .attr = { .name = "status", .mode = 0444 },
    .show = status_show,
    .store = NULL,
};

static struct attribute *sample_default_attrs[] = {
    &attr_baud.attr,
    &attr_status.attr,
    NULL,
};
ATTRIBUTE_GROUPS(sample_default);

/* ── Тип об'єкта kobj_type ──────────────────────────────────────────────── */
static const struct kobj_type sample_ktype = {
    .release        = sample_device_release,
    .sysfs_ops      = &sample_sysfs_ops,
    .default_groups = sample_default_groups,
};

static struct sample_device *g_device = NULL;

/* ── Ініціалізація та вивантаження модуля ───────────────────────────────── */
static int __init sample_module_init(void)
{
    int ret;
    pr_info("sample_device: initializing module\n");

    /* 1. Виділення пам'яті під зовнішній контейнер */
    g_device = kzalloc(sizeof(*g_device), GFP_KERNEL);
    if (!g_device)
        return -ENOMEM;

    g_device->dev_id = 42;
    g_device->baud_rate = 115200;
    strscpy(g_device->status_str, "OPERATIONAL_OK", sizeof(g_device->status_str));

    /* 2. Ініціалізація kobject та створення каталогу в /sys/kernel/ */
    ret = kobject_init_and_add(&g_device->kobj, &sample_ktype, kernel_kobj, "sample_device");
    if (ret) {
        pr_err("sample_device: failed to create kobject (err=%d)\n", ret);
        /* kobject_put обов'язковий навіть при збої додавання для очищення імені */
        kobject_put(&g_device->kobj);
        g_device = NULL;
        return ret;
    }

    pr_info("sample_device: registered successfully at /sys/kernel/sample_device/\n");
    return 0;
}

static void __exit sample_module_exit(void)
{
    pr_info("sample_device: exiting module, tearing down kobject\n");
    if (g_device) {
        /* 1. Видалення каталогу з sysfs (блокує нові open/read/write) */
        kobject_del(&g_device->kobj);

        /* 2. Скидання власного посилання модуля.
         * Коли всі відкриті дескриптори закриються, ядро викличе sample_device_release() */
        kobject_put(&g_device->kobj);
        g_device = NULL;
    }
}

module_init(sample_module_init);
module_exit(sample_module_exit);
