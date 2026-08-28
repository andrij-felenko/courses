// SPDX-License-Identifier: GPL-2.0
/*
 * msi_x_demo_driver.c — Каркас багаточергового драйвера з підтримкою MSI-X
 */

#include <linux/module.h>
#include <linux/pci.h>
#include <linux/interrupt.h>
#include <linux/kernel.h>
#include <linux/slab.h>

#define DRIVER_NAME "msix_demo_pci"
#define MAX_HW_QUEUES 8

struct queue_context {
    unsigned int queue_id;
    unsigned int irq;
    atomic_t interrupt_count;
    struct demo_device *parent;
};

struct demo_device {
    struct pci_dev *pdev;
    void __iomem *bar0_mmio;
    unsigned int num_allocated_irqs;
    struct queue_context queues[MAX_HW_QUEUES];
};

/* Обробник переривання конкретної черги (верхня половина) */
static irqreturn_t demo_queue_isr(int irq, void *dev_id)
{
    struct queue_context *q = (struct queue_context *)dev_id;

    /* Збільшуємо локальний лічильник оброблених подій */
    atomic_inc(&q->interrupt_count);

    /*
     * Оскільки для MSI-X переривання є фронтальним (edge-triggered)
     * та унікальним для кожної черги, читати статусний регістр через MMIO
     * для підтвердження факту події не потрібно.
     */
    return IRQ_HANDLED;
}

static int demo_pci_probe(struct pci_dev *pdev, const struct pci_device_id *id)
{
    struct demo_device *priv;
    int err, allocated, i;
    unsigned int nvec = min_t(unsigned int, num_online_cpus(), MAX_HW_QUEUES);

    dev_info(&pdev->dev, "Знайдено пристрій PCIe, запит на %u черг\n", nvec);

    err = pci_enable_device(pdev);
    if (err) {
        dev_err(&pdev->dev, "Помилка увімкнення пристрою: %d\n", err);
        return err;
    }

    pci_set_master(pdev);

    priv = kzalloc(sizeof(*priv), GFP_KERNEL);
    if (!priv) {
        err = -ENOMEM;
        goto err_disable;
    }
    priv->pdev = pdev;
    pci_set_drvdata(pdev, priv);

    err = pci_request_regions(pdev, DRIVER_NAME);
    if (err) {
        dev_err(&pdev->dev, "Не вдалося виділити MMIO-регіони: %d\n", err);
        goto err_free_priv;
    }

    priv->bar0_mmio = pci_iomap(pdev, 0, 0);
    if (!priv->bar0_mmio) {
        dev_err(&pdev->dev, "Помилка відображення BAR0\n");
        err = -EIO;
        goto err_release_regions;
    }

    /*
     * Виділення векторів переривань:
     * Просимо від 1 до nvec векторів із пріоритетом MSI-X.
     * Прапорець PCI_IRQ_AFFINITY автоматично розподіляє вектори по NUMA-вузлах.
     */
    allocated = pci_alloc_irq_vectors(pdev, 1, nvec,
                                      PCI_IRQ_MSIX | PCI_IRQ_MSI |
                                      PCI_IRQ_LEGACY | PCI_IRQ_AFFINITY);
    if (allocated < 0) {
        dev_err(&pdev->dev, "Не вдалося виділити переривання: %d\n", allocated);
        err = allocated;
        goto err_unmap;
    }

    priv->num_allocated_irqs = allocated;
    dev_info(&pdev->dev, "Успішно виділено %d векторів переривань\n", allocated);

    /* Реєстрація обробника для кожного виділеного вектора */
    for (i = 0; i < allocated; i++) {
        struct queue_context *q = &priv->queues[i];
        q->queue_id = i;
        q->parent = priv;
        q->irq = pci_irq_vector(pdev, i);
        atomic_set(&q->interrupt_count, 0);

        err = request_irq(q->irq, demo_queue_isr, 0, DRIVER_NAME, q);
        if (err) {
            dev_err(&pdev->dev, "Помилка request_irq для вектора %d (IRQ %u): %d\n",
                    i, q->irq, err);
            while (--i >= 0) {
                free_irq(priv->queues[i].irq, &priv->queues[i]);
            }
            goto err_free_vectors;
        }
    }

    return 0;

err_free_vectors:
    pci_free_irq_vectors(pdev);
err_unmap:
    pci_iounmap(pdev, priv->bar0_mmio);
err_release_regions:
    pci_release_regions(pdev);
err_free_priv:
    kfree(priv);
err_disable:
    pci_disable_device(pdev);
    return err;
}

static void demo_pci_remove(struct pci_dev *pdev)
{
    struct demo_device *priv = pci_get_drvdata(pdev);
    int i;

    dev_info(&pdev->dev, "Видалення драйвера, звільнення переривань\n");

    for (i = 0; i < priv->num_allocated_irqs; i++) {
        free_irq(priv->queues[i].irq, &priv->queues[i]);
    }

    pci_free_irq_vectors(pdev);
    pci_iounmap(pdev, priv->bar0_mmio);
    pci_release_regions(pdev);
    kfree(priv);
    pci_disable_device(pdev);
}

static const struct pci_device_id demo_pci_ids[] = {
    { PCI_DEVICE(0x10ee, 0x9038) }, /* Тестовий ідентифікатор FPGA/NIC */
    { 0, }
};
MODULE_DEVICE_TABLE(pci, demo_pci_ids);

static struct pci_driver demo_driver = {
    .name = DRIVER_NAME,
    .id_table = demo_pci_ids,
    .probe = demo_pci_probe,
    .remove = demo_pci_remove,
};

module_pci_driver(demo_driver);

MODULE_AUTHOR("Unix & Linux Systems Team");
MODULE_DESCRIPTION("Демонстраційний драйвер PCIe з підтримкою MSI-X");
MODULE_LICENSE("GPL");
