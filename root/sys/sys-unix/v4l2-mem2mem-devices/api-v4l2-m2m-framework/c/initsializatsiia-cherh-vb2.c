static int queue_init(void *priv, struct vb2_queue *src_vq, struct vb2_queue *dst_vq) {
    struct my_ctx *ctx = priv;
    int ret;

    /* 1. Налаштування вхідної черги (OUTPUT) */
    src_vq->type = V4L2_BUF_TYPE_VIDEO_OUTPUT_MPLANE;
    src_vq->io_modes = VB2_MMAP | VB2_DMABUF;
    src_vq->drv_priv = ctx;
    src_vq->buf_struct_size = sizeof(struct v4l2_m2m_buffer);
    src_vq->ops = &my_qops;
    src_vq->mem_ops = &vb2_dma_contig_memops;
    src_vq->timestamp_flags = V4L2_BUF_FLAG_TIMESTAMP_COPY;
    src_vq->lock = &ctx->q_lock;
    src_vq->dev = ctx->dev->dev;
    ret = vb2_queue_init(src_vq);
    if (ret)
        return ret;

    /* 2. Налаштування вихідної черги (CAPTURE) */
    dst_vq->type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
    dst_vq->io_modes = VB2_MMAP | VB2_DMABUF;
    dst_vq->drv_priv = ctx;
    dst_vq->buf_struct_size = sizeof(struct v4l2_m2m_buffer);
    dst_vq->ops = &my_qops;
    dst_vq->mem_ops = &vb2_dma_contig_memops;
    dst_vq->timestamp_flags = V4L2_BUF_FLAG_TIMESTAMP_COPY;
    dst_vq->lock = &ctx->q_lock;
    dst_vq->dev = ctx->dev->dev;
    return vb2_queue_init(dst_vq);
}
