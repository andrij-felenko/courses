struct dma_buf_ops {
        bool cache_sgt_mapping;
        int  (*attach)(struct dma_buf *, struct dma_buf_attachment *);
        void (*detach)(struct dma_buf *, struct dma_buf_attachment *);
        int  (*pin)(struct dma_buf_attachment *attach);
        void (*unpin)(struct dma_buf_attachment *attach);
        struct sg_table *(*map_dma_buf)(struct dma_buf_attachment *,
                                        enum dma_data_direction);
        void (*unmap_dma_buf)(struct dma_buf_attachment *, struct sg_table *,
                              enum dma_data_direction);
        void (*release)(struct dma_buf *);
        int  (*begin_cpu_access)(struct dma_buf *, enum dma_data_direction);
        int  (*end_cpu_access)(struct dma_buf *, enum dma_data_direction);
        int  (*mmap)(struct dma_buf *, struct vm_area_struct *vma);
        int  (*vmap)(struct dma_buf *dmabuf, struct iosys_map *map);
        void (*vunmap)(struct dma_buf *dmabuf, struct iosys_map *map);
};
