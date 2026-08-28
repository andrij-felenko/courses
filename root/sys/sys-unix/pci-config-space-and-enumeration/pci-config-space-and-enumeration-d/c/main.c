#include <linux/module.h>
#include <linux/pci.h>

/* Таблиця підтримуваних пристроїв */
static const struct pci_device_id my_pci_ids[] = {
    { PCI_DEVICE(0x8086, 0x10d3) }, /* Конкретний Vendor ID та Device ID */
    { 0, } /* Завершення таблиці */
};
MODULE_DEVICE_TABLE(pci, my_pci_ids);

/* Функція, що викликається, коли ядро знаходить сумісний пристрій */
static int my_pci_probe(struct pci_dev *pdev, const struct pci_device_id *id)
{
    int err;

    /* Вмикаємо пристрій (пробуджуємо з D3hot, вмикаємо BAR) */
    err = pci_enable_device(pdev);
    if (err) return err;

    /* Запитуємо регіони пам'яті (щоб інший драйвер їх не зайняв) */
    err = pci_request_regions(pdev, "my_driver");
    if (err) goto err_disable;

    /* ... тут мапимо BAR у віртуальну пам'ять — pci_iomap(pdev, 0, 0) —
       і працюємо з регістрами через ioread32()/iowrite32() ... */

    pr_info("my_driver: Знайдено пристрій!\n");
    return 0;

err_disable:
    pci_disable_device(pdev);
    return err;
}

/* Функція відключення (видалення модуля або гаряче витягання) */
static void my_pci_remove(struct pci_dev *pdev)
{
    pci_release_regions(pdev);
    pci_disable_device(pdev);
    pr_info("my_driver: Пристрій відключено\n");
}

static struct pci_driver my_pci_driver = {
    .name     = "my_driver",
    .id_table = my_pci_ids,
    .probe    = my_pci_probe,
    .remove   = my_pci_remove,
};

module_pci_driver(my_pci_driver);
MODULE_LICENSE("GPL");
