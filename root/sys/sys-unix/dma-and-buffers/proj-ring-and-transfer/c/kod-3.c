static unsigned int ring_free(const struct engine *e)
{
        return RING_LEN - 1 - ((e->tail - e->head) & (RING_LEN - 1));
}

static int engine_submit(struct engine *e, struct xfer *x)
{
        struct scatterlist *sg;
        unsigned long irqflags;
        int i, ret;

        /* 1. Віддаємо буфер пристроєві. Від цього рядка й до unmap
              процесор не має права ні читати його, ні писати.        */
        ret = dma_map_sgtable(e->dev, x->sgt, x->dir, 0);
        if (ret)
                return ret;               /* 0 або -EINVAL/-ENOMEM: перевірку не обійти */

        spin_lock_irqsave(&e->lock, irqflags);

        if (ring_free(e) < x->sgt->nents) {
                spin_unlock_irqrestore(&e->lock, irqflags);
                dma_unmap_sgtable(e->dev, x->sgt, x->dir, 0);   /* той самий напрямок */
                return -EBUSY;
        }

        /* 2. Обхід — по nents, кількості сегментів ПІСЛЯ відображення. */
        for_each_sgtable_dma_sg(x->sgt, sg, i) {
                struct hw_desc *d = &e->ring[e->tail];
                u32 fl = DESC_OWN;

                d->addr = cpu_to_le64(sg_dma_address(sg));
                d->len  = cpu_to_le32(sg_dma_len(sg));

                if (i == (int)x->sgt->nents - 1)
                        fl |= DESC_EOR;
                e->owner[e->tail] = (fl & DESC_EOR) ? x : NULL;

                /* 3. Адреса й довжина мусять лягти в пам'ять ДО прапорця,
                      який віддає дескриптор пристроєві.                  */
                dma_wmb();
                d->flags = cpu_to_le32(fl);

                e->tail = (e->tail + 1) & (RING_LEN - 1);
        }

        /* 4. Дзвінок у двері. */
        writel(e->tail, e->regs + REG_TAIL);

        spin_unlock_irqrestore(&e->lock, irqflags);
        return 0;
}
