static irqreturn_t myeth_isr(int irq, void *data)
{
        struct myeth *priv = data;
        u32 cause = readl(priv->regs + REG_IRQ_CAUSE);

        if (cause == 0)
                return IRQ_NONE;        /* не наше: лінія спільна */

        writel(cause, priv->regs + REG_IRQ_CAUSE);
        readl(priv->regs + REG_IRQ_CAUSE);      /* проштовхнути скидання */

        return IRQ_HANDLED;
}
