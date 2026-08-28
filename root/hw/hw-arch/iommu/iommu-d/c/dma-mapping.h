#include <linux/dma-mapping.h>

/* Буфер на 16 КБ, куди мережева карта клатиме вхідний пакет. */
void *cpu_buf = kmalloc(16384, GFP_KERNEL);   /* адреса для ЯДРА */

/* Попросити ядро завести переклад в IOMMU й повернути адресу ДЛЯ ПРИСТРОЮ. */
dma_addr_t dev_addr = dma_map_single(dev, cpu_buf, 16384, DMA_FROM_DEVICE);
if (dma_mapping_error(dev, dev_addr))
    return -ENOMEM;               /* IOMMU не зміг завести переклад */

/* Пристрій отримує САМЕ dev_addr (це IOVA), а не cpu_buf: */
iowrite32(dev_addr, dev->regs + REG_RX_BUF);   /* тепер DMA пише за IOVA  */
iowrite32(16384,    dev->regs + REG_RX_LEN);
/* ... карта виконала DMA й підняла переривання «готово» ... */

/* Зняти переклад: викреслити запис в IOMMU + знеправити IOTLB. */
dma_unmap_single(dev, dev_addr, 16384, DMA_FROM_DEVICE);
