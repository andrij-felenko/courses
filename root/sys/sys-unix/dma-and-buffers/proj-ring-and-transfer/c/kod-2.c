static int engine_start(struct engine *e)
{
        int ret;

        /* Досяжність оголошують ДО першого відображення: далі ядро саме
           вирішить, чи потрібен цьому пристрою підмінний буфер.        */
        ret = dma_set_mask_and_coherent(e->dev, DMA_BIT_MASK(64));
        if (ret)
                return ret;

        e->ring = dma_alloc_coherent(e->dev, RING_LEN * sizeof(*e->ring),
                                     &e->ring_dma, GFP_KERNEL);
        if (!e->ring)                     /* саме NULL: тут dma_mapping_error не треба */
                return -ENOMEM;

        spin_lock_init(&e->lock);
        e->head = e->tail = 0;

        writel(lower_32_bits(e->ring_dma), e->regs + REG_RING_LO);
        writel(upper_32_bits(e->ring_dma), e->regs + REG_RING_HI);
        return 0;
}
