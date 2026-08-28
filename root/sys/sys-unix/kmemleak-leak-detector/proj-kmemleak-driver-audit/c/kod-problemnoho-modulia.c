#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/slab.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Audit Test");
MODULE_DESCRIPTION("Buggy Driver for Kmemleak Audit");

struct dummy_ring {
    size_t capacity;
    u8 *data;
};

struct dummy_dev {
    int id;
    struct dummy_ring *ring;
};

static struct dummy_dev *g_device = NULL;

static int __init dummy_init(void)
{
    pr_info("dummy_leak_driver: Ініціалізація модуля...\n");

    /* 1. Виділяємо головну структуру пристрою */
    g_device = kmalloc(sizeof(struct dummy_dev), GFP_KERNEL);
    if (!g_device)
        return -ENOMEM;

    g_device->id = 42;

    /* 2. Виділяємо структуру кільцевого буфера */
    g_device->ring = kmalloc(sizeof(struct dummy_ring), GFP_KERNEL);
    if (!g_device->ring) {
        kfree(g_device);
        return -ENOMEM;
    }

    /* 3. Виділяємо буфер даних на 2048 байтів */
    g_device->ring->capacity = 2048;
    g_device->ring->data = kmalloc(g_device->ring->capacity, GFP_KERNEL);
    if (!g_device->ring->data) {
        kfree(g_device->ring);
        kfree(g_device);
        return -ENOMEM;
    }

    pr_info("dummy_leak_driver: Успішно завантажено, dev=%px, ring=%px, data=%px\n",
            g_device, g_device->ring, g_device->ring->data);
    return 0;
}

static void __exit dummy_exit(void)
{
    pr_info("dummy_leak_driver: Вивантаження модуля...\n");

    if (g_device) {
        if (g_device->ring) {
            /* ПОМИЛКА 1: Забули звільнити g_device->ring->data ! */
            kfree(g_device->ring);
        }
        /* ПОМИЛКА 2: Звільняємо g_device, втрачаючи посилання на data */
        kfree(g_device);
        g_device = NULL;
    }

    pr_info("dummy_leak_driver: Модуль вивантажено.\n");
}

module_init(dummy_init);
module_exit(dummy_exit);
