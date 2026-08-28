/* skb з готовим пакетом на відправлення. */
dma_addr_t da = dma_map_single(dev, skb->data, skb->len, DMA_TO_DEVICE);
if (dma_mapping_error(dev, da))          /* IOVA скінчились чи мапінг не вдався */
    return -ENOMEM;

desc->addr = cpu_to_le64(da);            /* карті — IOVA, а НЕ skb->data! */
desc->len  = cpu_to_le32(skb->len);
dma_wmb();                               /* дескриптор видимий ДО дзвінка */
desc->status = cpu_to_le32(DESC_OWN_NIC);
iowrite32(tx_tail, regs + REG_TX_TAIL);  /* дзвінок: «є що слати» */

/* ... карта відіслала пакет і підняла переривання «готово» ... */
dma_unmap_single(dev, da, skb->len, DMA_TO_DEVICE);
dev_kfree_skb(skb);
