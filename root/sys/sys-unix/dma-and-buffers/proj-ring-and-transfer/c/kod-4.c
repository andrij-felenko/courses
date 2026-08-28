static irqreturn_t engine_irq(int irq, void *data)
{
        struct engine *e = data;
        unsigned int handled = 0;

        spin_lock(&e->lock);              /* переривання на цьому ядрі вже вимкнено */

        while (e->head != e->tail) {
                struct hw_desc *d = &e->ring[e->head];
                struct xfer *x = e->owner[e->head];
                u32 fl = le32_to_cpu(READ_ONCE(d->flags));

                if (fl & DESC_OWN)        /* пристрій ще не віддав — далі не йдемо */
                        break;

                /* 5. Прапорець прочитано; лише тепер решта полів
                      цього дескриптора справді наша.               */
                dma_rmb();

                e->owner[e->head] = NULL;
                e->head = (e->head + 1) & (RING_LEN - 1);
                handled++;

                if (!x)                   /* проміжний сегмент запиту */
                        continue;

                /* 6. Ті самі аргументи, що й при відображенні. Тільки
                      після цього рядка вміст буфера можна читати.    */
                dma_unmap_sgtable(e->dev, x->sgt, x->dir, 0);
                x->done(x, (fl & DESC_ERR) ? -EIO : 0);
        }

        spin_unlock(&e->lock);

        if (!handled)
                return IRQ_NONE;          /* переривання не наше: лінію ділять */
        writel(1, e->regs + REG_IRQ_ACK);
        return IRQ_HANDLED;
}
