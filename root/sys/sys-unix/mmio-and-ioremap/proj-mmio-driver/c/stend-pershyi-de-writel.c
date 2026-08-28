static void myeth_kick_batch(struct myeth *p, dma_addr_t buf, u32 len,
                             unsigned int n)
{
        unsigned int i, first = p->head;

        for (i = 0; i < n; i++) {
                struct tx_desc *d = &p->ring[(first + i) % RING_LEN];

                d->addr  = cpu_to_le64(buf);
                d->len   = cpu_to_le32(len);
                d->flags = DESC_OWN;
        }

        /* Один бар'єр на всю пачку: він відділяє ВСІ записи в кільце
           від ВСІХ дзвінків, а дзвінки впорядковані між собою самі. */
        dma_wmb();
        for (i = 0; i < n; i++)
                writel_relaxed((first + i) % RING_LEN, p->regs + REG_TX_KICK);

        p->head = (first + n) % RING_LEN;
        p->sent += n;
}
