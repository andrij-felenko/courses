dma_addr_t dma_map_single_attrs(struct device *dev, void *ptr, size_t size,
                                enum dma_data_direction dir, unsigned long attrs);
void       dma_unmap_single_attrs(struct device *dev, dma_addr_t addr, size_t size,
                                  enum dma_data_direction dir, unsigned long attrs);

dma_addr_t dma_map_page_attrs(struct device *dev, struct page *page, size_t offset,
                              size_t size, enum dma_data_direction dir,
                              unsigned long attrs);
void       dma_unmap_page_attrs(struct device *dev, dma_addr_t addr, size_t size,
                                enum dma_data_direction dir, unsigned long attrs);

#define dma_map_single(d, a, s, r)     dma_map_single_attrs(d, a, s, r, 0)
#define dma_unmap_single(d, a, s, r)   dma_unmap_single_attrs(d, a, s, r, 0)
#define dma_map_page(d, p, o, s, r)    dma_map_page_attrs(d, p, o, s, r, 0)
#define dma_unmap_page(d, a, s, r)     dma_unmap_page_attrs(d, a, s, r, 0)
