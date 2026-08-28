#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/pci.h>
#include <linux/interrupt.h>

#define MY_VENDOR_ID 0x8086
#define MY_DEVICE_ID 0x100e

struct my_driver_priv {
    void __iomem *hw_addr;
    int irq_vec;
};

static irqreturn_t my_pci_interrupt_handler(int irq, void *dev_id) {
    struct my_driver_priv *priv = dev_id;
    u32 status = readl(priv->hw_addr + 0x08); /* Читання статусного регістра */
    if (!status) return IRQ_NONE;
    
    writel(status, priv->hw_addr + 0x08); /* Очищення переривання (Write-1-to-Clear) */
    return IRQ_HANDLED;
}

static int my_pci_probe(struct pci_dev *pdev, const struct pci_device_id *id) {
    struct my_driver_priv *priv;
    int err;

    err = pci_enable_device(pdev);
    if (err) return err;

    err = pci_request_regions(pdev, "my_pci_driver");
    if (err) goto err_disable;

    pci_set_master(pdev);

    priv = kzalloc(sizeof(*priv), GFP_KERNEL);
    if (!priv) {
        err = -ENOMEM;
        goto err_release;
    }

    priv->hw_addr = pci_iomap(pdev, 0, 0);
    if (!priv->hw_addr) {
        err = -EIO;
        goto err_free_priv;
    }

    err = pci_alloc_irq_vectors(pdev, 1, 1, PCI_IRQ_MSIX | PCI_IRQ_MSI);
    if (err < 0) goto err_iounmap;

    priv->irq_vec = pci_irq_vector(pdev, 0);
    err = request_irq(priv->irq_vec, my_pci_interrupt_handler, 0, "my_pci_driver", priv);
    if (err) goto err_free_irq;

    pci_set_drvdata(pdev, priv);
    dev_info(&pdev->dev, "Пристрій PCI успішно ініціалізовано\n");
    return 0;

err_free_irq:
    pci_free_irq_vectors(pdev);
err_iounmap:
    pci_iounmap(pdev, priv->hw_addr);
err_free_priv:
    kfree(priv);
err_release:
    pci_release_regions(pdev);
err_disable:
    pci_disable_device(pdev);
    return err;
}

static void my_pci_remove(struct pci_dev *pdev) {
    struct my_driver_priv *priv = pci_get_drvdata(pdev);

    free_irq(priv->irq_vec, priv);
    pci_free_irq_vectors(pdev);
    pci_iounmap(pdev, priv->hw_addr);
    kfree(priv);
    pci_release_regions(pdev);
    pci_disable_device(pdev);
    dev_info(&pdev->dev, "Пристрій PCI вивантажено\n");
}

static const struct pci_device_id my_pci_ids[] = {
    { PCI_DEVICE(MY_VENDOR_ID, MY_DEVICE_ID) },
    { 0, }
};
MODULE_DEVICE_TABLE(pci, my_pci_ids);

static struct pci_driver my_driver = {
    .name = "my_pci_driver",
    .id_table = my_pci_ids,
    .probe = my_pci_probe,
    .remove = my_pci_remove,
};

module_pci_driver(my_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Unix-Linux Reference Author");
MODULE_DESCRIPTION("Приклад базового драйвера PCI для Linux");
