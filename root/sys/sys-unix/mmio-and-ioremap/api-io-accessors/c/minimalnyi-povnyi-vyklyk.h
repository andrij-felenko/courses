/* один раз, при прив'язці: займає діапазон, відображає, чіпляє звільнення */
priv->regs = devm_platform_ioremap_resource(pdev, 0);
if (IS_ERR(priv->regs))
        return PTR_ERR(priv->regs);

/* дескриптор у звичайній пам'яті — і команда пристроєві;
   бар'єр між ними несе сам writel, писати його вручну не треба */
desc->flags = cpu_to_le32(DESC_OWN);
writel(TX_KICK_GO, priv->regs + REG_TX_KICK);

/* скидання причини переривання — і зустрічне читання, щоб запис дійшов */
writel(cause, priv->regs + REG_IRQ_CAUSE);
readl(priv->regs + REG_IRQ_CAUSE);
