unsigned int dma_map_sg_attrs(struct device *dev, struct scatterlist *sg, int nents,
                              enum dma_data_direction dir, unsigned long attrs);
void         dma_unmap_sg_attrs(struct device *dev, struct scatterlist *sg, int nents,
                                enum dma_data_direction dir, unsigned long attrs);

int  dma_map_sgtable(struct device *dev, struct sg_table *sgt,
                     enum dma_data_direction dir, unsigned long attrs);
void dma_unmap_sgtable(struct device *dev, struct sg_table *sgt,
                       enum dma_data_direction dir, unsigned long attrs);

#define dma_map_sg(d, s, n, r)    dma_map_sg_attrs(d, s, n, r, 0)
#define dma_unmap_sg(d, s, n, r)  dma_unmap_sg_attrs(d, s, n, r, 0)
