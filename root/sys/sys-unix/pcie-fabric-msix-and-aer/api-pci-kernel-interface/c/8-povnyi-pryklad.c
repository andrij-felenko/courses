#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/pci.h>
#include <linux/interrupt.h>

#define DRV_NAME "example_pcie_driver"
#define MY_VENDOR_ID 0x10de  /* Приклад Vendor ID */
#define MY_DEVICE_ID 0x1cb3  /* Приклад Device ID */

struct my_driver_priv {
    struct pci_dev *pdev;
    void __iomem *bar0_mmio;
    u8 *dma_cpu_buf;
    dma_addr_t dma_handle;
    int num_vectors;
};

static irqreturn_t my_pcie_isr(int irq, void *dev_id)
{
    struct my_driver_priv *priv = dev_id;
    u32 status;

    /* Читання регістра стану переривання з MMIO BAR0 */
    status = ioread32(priv->bar0_mmio + 0x10);
    if (!status)
        return IRQ_NONE;

    /* Квитування (очищення) переривання на пристрої */
    iowrite32(status, priv->bar0_mmio + 0x10);

    dev_info(&priv->pdev->dev, "Отримано MSI-X переривання, статус: 0x%08x\n", status);
    return IRQ_HANDLED;
}

static int my_pci_probe(struct pci_dev *pdev, const struct pci_device_id *id)
{
    struct my_driver_priv *priv;
    int ret, irq;

    dev_info(&pdev->dev, "Знайдено PCIe пристрій BDF %s\n", pci_name(pdev));

    /* 1. Створення приватного контексту драйвера */
    priv = devm_kzalloc(&pdev->dev, sizeof(*priv), GFP_KERNEL);
    if (!priv)
        return -ENOMEM;

    priv->pdev = pdev;
    pci_set_drvdata(pdev, priv);

    /* 2. Кероване активація пристрою (devres API) */
    ret = pcim_enable_device(pdev);
    if (ret) {
        dev_err(&pdev->dev, "Помилка виклику pcim_enable_device: %d\n", ret);
        return ret;
    }

    /* 3. Резервування та відображення саме BAR0 (маска BIT(0)) */
    ret = pcim_iomap_regions(pdev, BIT(0), DRV_NAME);
    if (ret) {
        dev_err(&pdev->dev, "Не вдалося зарезервувати BAR0: %d\n", ret);
        return ret;
    }

    /* 4. Отримання віртуальної адреси MMIO BAR0 */
    priv->bar0_mmio = pcim_iomap_table(pdev)[0];
    if (!priv->bar0_mmio) {
        dev_err(&pdev->dev, "Помилка відображення BAR0 в MMIO\n");
        return -ENOMEM;
    }

    /* 5. Увімкнення Bus Master для проведення DMA */
    pci_set_master(pdev);

    /* 6. Налаштування маски DMA (спочатку 64-біт, при відмові — 32-біт) */
    ret = dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(64));
    if (ret) {
        ret = dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(32));
        if (ret) {
            dev_err(&pdev->dev, "Апаратура не підтримує доступну розрядність DMA\n");
            return ret;
        }
    }

    /* 7. Виділення когерентного DMA буфера на 4096 байт */
    priv->dma_cpu_buf = dma_alloc_coherent(&pdev->dev, 4096, &priv->dma_handle, GFP_KERNEL);
    if (!priv->dma_cpu_buf) {
        dev_err(&pdev->dev, "Не вдалося виділити когерентний DMA буфер\n");
        return -ENOMEM;
    }

    /* 8. Виділення векторів переривань MSI-X / MSI */
    ret = pci_alloc_irq_vectors(pdev, 1, 4, PCI_IRQ_ALL_TYPES);
    if (ret < 0) {
        dev_err(&pdev->dev, "Помилка виділення векторів переривань: %d\n", ret);
        goto err_dma_free;
    }
    priv->num_vectors = ret;

    /* 9. Реєстрація обробника для першого вектора IRQ */
    irq = pci_irq_vector(pdev, 0);
    ret = devm_request_irq(&pdev->dev, irq, my_pcie_isr, 0, DRV_NAME, priv);
    if (ret) {
        dev_err(&pdev->dev, "Не вдалося зареєструвати ISR для IRQ %d: %d\n", irq, ret);
        goto err_free_irq_vecs;
    }

    dev_info(&pdev->dev, "Драйвер успішно ініціалізовано. BAR0=%pr, IRQ=%d, DMA=0x%llx\n",
             &pdev->resource[0], irq, (unsigned long long)priv->dma_handle);
    return 0;

err_free_irq_vecs:
    pci_free_irq_vectors(pdev);
err_dma_free:
    dma_free_coherent(&pdev->dev, 4096, priv->dma_cpu_buf, priv->dma_handle);
    return ret;
}

static void my_pci_remove(struct pci_dev *pdev)
{
    struct my_driver_priv *priv = pci_get_drvdata(pdev);

    dev_info(&pdev->dev, "Вивантаження драйвера для BDF %s\n", pci_name(pdev));

    /* Зупинка апаратури та вимкнення Bus Master */
    pci_clear_master(pdev);

    /* Обробник знімаємо ДО звільнення векторів: devres звільнив би його
       лише після повернення з remove(), коли вектора вже не існує */
    devm_free_irq(&pdev->dev, pci_irq_vector(pdev, 0), priv);

    /* Звільнення векторів переривань та DMA буфера */
    pci_free_irq_vectors(pdev);
    if (priv->dma_cpu_buf)
        dma_free_coherent(&pdev->dev, 4096, priv->dma_cpu_buf, priv->dma_handle);

    /* Звільнення MMIO та disable_device виконуються devres автоматично */
}

static const struct pci_device_id my_pci_ids[] = {
    { PCI_DEVICE(MY_VENDOR_ID, MY_DEVICE_ID) },
    { 0, }
};
MODULE_DEVICE_TABLE(pci, my_pci_ids);

static struct pci_driver my_driver = {
    .name = DRV_NAME,
    .id_table = my_pci_ids,
    .probe = my_pci_probe,
    .remove = my_pci_remove,
};

module_pci_driver(my_driver);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Course Linux Kernel Developer");
MODULE_DESCRIPTION("Довідковий драйвер PCI Express для ядра Linux");
