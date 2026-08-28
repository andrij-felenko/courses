/* виділення кільця — один раз, при під'єднанні пристрою */
struct desc *ring = dma_alloc_coherent(dev, RING_BYTES, &ring_dma, GFP_KERNEL);
if (!ring)
        return -ENOMEM;

/* передача одного блоку — щоразу */
dma_addr_t da = dma_map_single(dev, buf, len, DMA_TO_DEVICE);
if (dma_mapping_error(dev, da))          /* нуль тут — законна адреса, тому окрема перевірка */
        return -EIO;

ring[i].addr = cpu_to_le64(da);          /* пристрій читає числа у своєму порядку байтів */
ring[i].len  = cpu_to_le32(len);
wmb();                                   /* дескриптор має лягти в пам'ять ДО дзвінка пристрою */
writel(i + 1, regs + REG_TAIL);          /* «є робота» */

/* у перериванні про завершення */
dma_unmap_single(dev, da, len, DMA_TO_DEVICE);
