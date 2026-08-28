#include <linux/refcount.h>

struct kernel_device_data {
    refcount_t refcount;
    char buffer[128];
};

struct kernel_device_data *device_alloc(void)
{
    struct kernel_device_data *dev = kmalloc(sizeof(*dev), GFP_KERNEL);
    if (!dev)
        return NULL;

    // Ініціалізація початкового значення refcount = 1
    refcount_set(&dev->refcount, 1);
    return dev;
}

void device_get(struct kernel_device_data *dev)
{
    // Безпечне збільшення лічильника посилань
    refcount_inc(&dev->refcount);
}

void device_put(struct kernel_device_data *dev)
{
    // Зменшує і перевіряє на 0
    if (refcount_dec_and_test(&dev->refcount)) {
        kfree(dev);
    }
}
