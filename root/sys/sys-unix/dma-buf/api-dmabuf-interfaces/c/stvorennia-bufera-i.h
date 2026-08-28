struct dma_buf_export_info {
        const char *exp_name;            /* ім'я для debugfs і fdinfo */
        struct module *owner;            /* тримає модуль, доки живий буфер */
        const struct dma_buf_ops *ops;
        size_t size;
        int flags;                       /* режим файла: типово O_RDWR */
        struct dma_resv *resv;           /* NULL — ядро заведе власний */
        void *priv;                      /* контекст експортера */
};

#define DEFINE_DMA_BUF_EXPORT_INFO(name)                                \
        struct dma_buf_export_info name = { .exp_name = KBUILD_MODNAME, \
                                         .owner = THIS_MODULE }

struct dma_buf *dma_buf_export(const struct dma_buf_export_info *exp_info);
int             dma_buf_fd(struct dma_buf *dmabuf, int flags);
