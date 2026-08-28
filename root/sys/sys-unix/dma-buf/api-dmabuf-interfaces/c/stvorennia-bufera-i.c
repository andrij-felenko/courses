DEFINE_DMA_BUF_EXPORT_INFO(info);
info.ops   = &my_ops;
info.size  = len;
info.flags = O_RDWR;
info.priv  = buf;

struct dma_buf *dmabuf = dma_buf_export(&info);
if (IS_ERR(dmabuf))
        return PTR_ERR(dmabuf);

int fd = dma_buf_fd(dmabuf, O_CLOEXEC);
if (fd < 0) {
        dma_buf_put(dmabuf);      /* лише на цій гілці */
        return fd;
}
return fd;                        /* далі посилання належить дескрипторові */
