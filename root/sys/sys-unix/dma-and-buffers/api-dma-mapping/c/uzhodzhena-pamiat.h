void *dma_alloc_attrs(struct device *dev, size_t size, dma_addr_t *dma_handle,
                      gfp_t flag, unsigned long attrs);
void  dma_free_attrs(struct device *dev, size_t size, void *cpu_addr,
                     dma_addr_t dma_handle, unsigned long attrs);

static inline void *dma_alloc_coherent(struct device *dev, size_t size,
                                       dma_addr_t *dma_handle, gfp_t gfp);
#define dma_free_coherent(d, s, c, h)  dma_free_attrs(d, s, c, h, 0)

static inline void *dma_alloc_wc(struct device *dev, size_t size,
                                 dma_addr_t *dma_addr, gfp_t gfp);  /* + WRITE_COMBINE */
