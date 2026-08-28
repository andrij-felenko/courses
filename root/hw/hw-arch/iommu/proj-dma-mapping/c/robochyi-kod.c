int n = dma_map_sg(dev, sglist, nents, DMA_TO_DEVICE);
if (n == 0)
    return -ENOMEM;

struct scatterlist *sg;
int i;
for_each_sg(sglist, sg, n, i) {
    desc[i].addr = cpu_to_le64(sg_dma_address(sg));   /* IOVA шматка */
    desc[i].len  = cpu_to_le32(sg_dma_len(sg));
}
/* ... передача ... */
dma_unmap_sg(dev, sglist, nents, DMA_TO_DEVICE);
