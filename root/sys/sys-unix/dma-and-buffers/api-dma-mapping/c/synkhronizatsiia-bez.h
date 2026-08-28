void dma_sync_single_for_cpu(struct device *dev, dma_addr_t addr, size_t size,
                             enum dma_data_direction dir);
void dma_sync_single_for_device(struct device *dev, dma_addr_t addr, size_t size,
                                enum dma_data_direction dir);
void dma_sync_sg_for_cpu(struct device *dev, struct scatterlist *sg, int nelems,
                         enum dma_data_direction dir);
void dma_sync_sg_for_device(struct device *dev, struct scatterlist *sg, int nelems,
                            enum dma_data_direction dir);
void dma_sync_sgtable_for_cpu(struct device *dev, struct sg_table *sgt,
                              enum dma_data_direction dir);
void dma_sync_sgtable_for_device(struct device *dev, struct sg_table *sgt,
                                 enum dma_data_direction dir);
