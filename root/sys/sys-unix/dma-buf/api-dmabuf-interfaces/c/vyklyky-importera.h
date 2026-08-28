struct dma_buf *dma_buf_get(int fd);
void            dma_buf_put(struct dma_buf *dmabuf);

struct dma_buf_attachment *dma_buf_attach(struct dma_buf *dmabuf,
                                          struct device *dev);
struct dma_buf_attachment *dma_buf_dynamic_attach(struct dma_buf *dmabuf,
                                          struct device *dev,
                                          const struct dma_buf_attach_ops *importer_ops,
                                          void *importer_priv);
void dma_buf_detach(struct dma_buf *dmabuf, struct dma_buf_attachment *attach);

int  dma_buf_pin(struct dma_buf_attachment *attach);
void dma_buf_unpin(struct dma_buf_attachment *attach);

struct sg_table *dma_buf_map_attachment(struct dma_buf_attachment *,
                                        enum dma_data_direction);
void dma_buf_unmap_attachment(struct dma_buf_attachment *, struct sg_table *,
                              enum dma_data_direction);
struct sg_table *dma_buf_map_attachment_unlocked(struct dma_buf_attachment *,
                                        enum dma_data_direction);
void dma_buf_unmap_attachment_unlocked(struct dma_buf_attachment *,
                                       struct sg_table *,
                                       enum dma_data_direction);

int  dma_buf_begin_cpu_access(struct dma_buf *, enum dma_data_direction dir);
int  dma_buf_end_cpu_access(struct dma_buf *, enum dma_data_direction dir);
int  dma_buf_mmap(struct dma_buf *, struct vm_area_struct *, unsigned long pgoff);

int  dma_buf_vmap(struct dma_buf *dmabuf, struct iosys_map *map);
void dma_buf_vunmap(struct dma_buf *dmabuf, struct iosys_map *map);
int  dma_buf_vmap_unlocked(struct dma_buf *dmabuf, struct iosys_map *map);
void dma_buf_vunmap_unlocked(struct dma_buf *dmabuf, struct iosys_map *map);
