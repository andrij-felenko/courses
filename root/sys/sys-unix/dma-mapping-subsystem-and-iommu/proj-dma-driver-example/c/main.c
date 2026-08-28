#include <linux/module.h>
#include <linux/init.h>
#include <linux/pci.h>
#include <linux/dma-mapping.h>
#include <linux/slab.h>

#define DRV_NAME "demo_dma_driver"
#define RING_SIZE 16
#define PKT_BUF_SIZE 2048

/* Апаратний дескриптор кільцевого буфера, що передається у DMA-реєстри пристрою */
struct demo_dma_desc {
    __le64 buf_addr;  /* Шинна адреса (IOVA) буфера корисного навантаження */
    __le32 len;       /* Довжина пакета в байтах */
    __le32 flags;     /* Прапорці стану: bit 0 — READY, bit 1 — COMPLETED */
};

/* Приватний контекст драйвера пристрою */
struct demo_device {
    struct pci_dev *pdev;
    
    /* Coherent DMA: кільцевий буфер дескрипторів */
    struct demo_dma_desc *ring_cpu;
    dma_addr_t ring_dma;
    size_t ring_size_bytes;

    /* Streaming DMA: відображення окремого пакета даних */
    void *tx_buf_cpu;
    dma_addr_t tx_buf_dma;
};

/* Крок 1. Узгодження та налаштування розрядності DMA-маски */
static int demo_setup_dma_masks(struct pci_dev *pdev)
{
    int err;

    /* Намагаємося встановити повноцінне 64-бітне адресування */
    err = dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(64));
    if (err) {
        dev_warn(&pdev->dev, "64-бітна DMA маска недоступна, спроба встановити 32-бітну\n");
        /* Якщо 64 біти не підтримуються материнською платою чи контролером, падаємо до 32 біт */
        err = dma_set_mask_and_coherent(&pdev->dev, DMA_BIT_MASK(32));
        if (err) {
            dev_err(&pdev->dev, "Не вдалося встановити жодну із сумісних DMA-масок!\n");
            return err;
        }
    }

    dev_info(&pdev->dev, "DMA маску пристрою успішно узгоджено з ядром\n");
    return 0;
}

/* Крок 2. Виділення Coherent пам'яті для кільця дескрипторів */
static int demo_alloc_ring(struct demo_device *demo)
{
    struct device *dev = &demo->pdev->dev;

    demo->ring_size_bytes = RING_SIZE * sizeof(struct demo_dma_desc);

    /* dma_alloc_coherent повертає пам'ять, когерентну для CPU і для пристрою */
    demo->ring_cpu = dma_alloc_coherent(dev, demo->ring_size_bytes,
                                       &demo->ring_dma, GFP_KERNEL);
    if (!demo->ring_cpu) {
        dev_err(dev, "Збій виділення coherent пам'яті для кільцевого буфера\n");
        return -ENOMEM;
    }

    /* Явне обнулення пам'яті кільця */
    memset(demo->ring_cpu, 0, demo->ring_size_bytes);

    dev_info(dev, "Виділено кільце дескрипторів: CPU addr=%p, DMA IOVA=%pad\n",
             demo->ring_cpu, &demo->ring_dma);
    return 0;
}

/* Крок 3. Потокове відображення буфера даних (Streaming DMA) */
static int demo_map_tx_packet(struct demo_device *demo)
{
    struct device *dev = &demo->pdev->dev;

    /* Виділяємо звичайний кешований буфер з загального сторінкового пулу */
    demo->tx_buf_cpu = kmalloc(PKT_BUF_SIZE, GFP_KERNEL);
    if (!demo->tx_buf_cpu)
        return -ENOMEM;

    /* Заповнюємо тестовими даними */
    memset(demo->tx_buf_cpu, 0xAB, PKT_BUF_SIZE);

    /* Здійснюємо потокове відображення у напрямку від CPU до пристрою */
    demo->tx_buf_dma = dma_map_single(dev, demo->tx_buf_cpu,
                                      PKT_BUF_SIZE, DMA_TO_DEVICE);

    /* Обов'язкова перевірка помилки через dma_mapping_error */
    if (dma_mapping_error(dev, demo->tx_buf_dma)) {
        dev_err(dev, "Збій виконання dma_map_single()\n");
        kfree(demo->tx_buf_cpu);
        demo->tx_buf_cpu = NULL;
        return -EIO;
    }

    /* Записуємо конвертовані у Little-Endian дані в дескриптор */
    demo->ring_cpu[0].buf_addr = cpu_to_le64(demo->tx_buf_dma);
    demo->ring_cpu[0].len      = cpu_to_le32(PKT_BUF_SIZE);
    demo->ring_cpu[0].flags    = cpu_to_le32(0x1); /* READY flag */

    dev_info(dev, "Пакет успішно відображено для DMA: IOVA=%pad\n", &demo->tx_buf_dma);
    return 0;
}

/* Крок 4. Приклад ручної синхронізації кешу CPU (DMA Sync) */
static void demo_update_packet_payload(struct demo_device *demo)
{
    struct device *dev = &demo->pdev->dev;

    /* Тимчасово забираємо володіння буфером назад у CPU */
    dma_sync_single_for_cpu(dev, demo->tx_buf_dma, PKT_BUF_SIZE, DMA_TO_DEVICE);

    /* Тепер CPU має право читати та змінювати вміст буфера */
    ((u8 *)demo->tx_buf_cpu)[0] = 0xFF;

    /* Повертаємо володіння буфером пристрою перед передачею контролю DMA */
    dma_sync_single_for_device(dev, demo->tx_buf_dma, PKT_BUF_SIZE, DMA_TO_DEVICE);
}

/* Крок 5. Скасування відображень та очищення ресурсів */
static void demo_cleanup_dma(struct demo_device *demo)
{
    struct device *dev = &demo->pdev->dev;

    /* 1. Скасовуємо потокове відображення пакета */
    if (demo->tx_buf_dma && !dma_mapping_error(dev, demo->tx_buf_dma)) {
        dma_unmap_single(dev, demo->tx_buf_dma, PKT_BUF_SIZE, DMA_TO_DEVICE);
        demo->tx_buf_dma = 0;
    }

    if (demo->tx_buf_cpu) {
        kfree(demo->tx_buf_cpu);
        demo->tx_buf_cpu = NULL;
    }

    /* 2. Звільняємо coherent пам'ять кільця дескрипторів */
    if (demo->ring_cpu) {
        dma_free_coherent(dev, demo->ring_size_bytes,
                          demo->ring_cpu, demo->ring_dma);
        demo->ring_cpu = NULL;
        demo->ring_dma = 0;
    }

    dev_info(dev, "Усі DMA ресурси пристрою успішно вилучено\n");
}

/* Демонстраційна точка входу модуля ядра */
static int __init demo_dma_init(void)
{
    pr_info("Завантаження демонстраційного модуля підсистеми DMA mapping\n");
    return 0;
}

static void __exit demo_dma_exit(void)
{
    pr_info("Вивантаження демонстраційного модуля підсистеми DMA mapping\n");
}

module_init(demo_dma_init);
module_exit(demo_dma_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Antigravity Team");
MODULE_DESCRIPTION("Демонстраційний модуль DMA Mapping та IOMMU в ядрі Linux");
