/*
 * p2p_dma_demo.c — Приклад модуля ядра Linux для тестування pci-p2pdma
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>
#include <linux/pci.h>
#include <linux/pci-p2pdma.h>
#include <linux/dma-mapping.h>
#include <linux/scatterlist.h>

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Antigravity Engineer");
MODULE_DESCRIPTION("PCIe P2PDMA Mapping Demo Driver");

// BDF пристроїв для прикладу (передаються як параметри модуля при insmod)
static char *provider_bdf = "0000:03:00.0"; // NVMe SSD з CMB
static char *client_bdf   = "0000:04:00.0"; // Ініціатор DMA (FPGA / SmartNIC)

module_param(provider_bdf, charp, 0644);
MODULE_PARM_DESC(provider_bdf, "PCI BDF of Provider Device (e.g. 0000:03:00.0)");
module_param(client_bdf, charp, 0644);
MODULE_PARM_DESC(client_bdf, "PCI BDF of Client Device (e.g. 0000:04:00.0)");

static struct pci_dev *provider_dev;
static struct pci_dev *client_dev;
static void *p2p_vaddr;
static struct scatterlist sg;

static int __init p2p_demo_init(void)
{
    int ret = 0;
    int dist;
    int nents;
    dma_addr_t dma_bus_addr;
    struct device *clients[1];

    pr_info("P2PDMA Demo: Початок ініціалізації драйвера\n");

    // 1. Пошук пристроїв за їхніми BDF в ірархії PCI
    provider_dev = pci_get_pfnblock(provider_bdf);
    if (!provider_dev) {
        pr_err("P2PDMA Demo: Не знайдено пристрій-провайдер %s\n", provider_bdf);
        return -ENODEV;
    }

    client_dev = pci_get_pfnblock(client_bdf);
    if (!client_dev) {
        pr_err("P2PDMA Demo: Не знайдено пристрій-клієнт %s\n", client_bdf);
        pci_dev_put(provider_dev);
        return -ENODEV;
    }

    // 2. Перевірка топологічної відстані та ACS сумісності
    clients[0] = &client_dev->dev;
    dist = pci_p2pdma_distance_many(provider_dev, clients, 1, true);
    if (dist < 0) {
        pr_err("P2PDMA Demo: P2P DMA НЕМОЖЛИВИЙ між %s та %s (dist=%d)\n",
               provider_bdf, client_bdf, dist);
        ret = -EIO;
        goto err_put;
    }

    pr_info("P2PDMA Demo: Обчислена топологічна відстань P2P: %d\n", dist);

    // 3. Виділення 4 КіБ пам'яті з P2P пулу провайдера
    p2p_vaddr = pci_alloc_p2pmem(provider_dev, PAGE_SIZE);
    if (!p2p_vaddr) {
        pr_err("P2PDMA Demo: Не вдалося виділити P2P пам'ять із пулу провайдера\n");
        ret = -ENOMEM;
        goto err_put;
    }

    pr_info("P2PDMA Demo: Виділено P2P буфер: vaddr=%px\n", p2p_vaddr);

    // 4. Ініціалізація структури scatterlist
    sg_init_table(&sg, 1);
    sg_set_page(&sg, virt_to_page(p2p_vaddr), PAGE_SIZE, 0);

    // 5. Мапування P2PDMA для клієнтського пристрою
    nents = pci_p2pdma_map_sg(&client_dev->dev, &sg, 1, DMA_BIDIRECTIONAL);
    if (nents <= 0) {
        pr_err("P2PDMA Demo: pci_p2pdma_map_sg повернув помилку (%d)\n", nents);
        ret = -EIO;
        goto err_free_mem;
    }

    // 6. Отримання шинної DMA-адреси для програмування регістрів апаратного DMA-контролера
    dma_bus_addr = sg_dma_address(&sg);
    pr_info("P2PDMA Demo: Успішно замаповано! Bus DMA Address = %pad\n", &dma_bus_addr);

    // Тут зазвичай виконується запис dma_bus_addr в регістри апаратного DMA-рушія client_dev
    return 0;

err_free_mem:
    pci_free_p2pmem(provider_dev, p2p_vaddr, PAGE_SIZE);
err_put:
    pci_dev_put(client_dev);
    pci_dev_put(provider_dev);
    return ret;
}

static void __exit p2p_demo_exit(void)
{
    pr_info("P2PDMA Demo: Завершення роботи та розвантаження модуля\n");
    if (p2p_vaddr) {
        pci_p2pdma_unmap_sg(&client_dev->dev, &sg, 1, DMA_BIDIRECTIONAL);
        pci_free_p2pmem(provider_dev, p2p_vaddr, PAGE_SIZE);
    }
    if (client_dev)
        pci_dev_put(client_dev);
    if (provider_dev)
        pci_dev_put(provider_dev);
}

module_init(p2p_demo_init);
module_exit(p2p_demo_exit);
