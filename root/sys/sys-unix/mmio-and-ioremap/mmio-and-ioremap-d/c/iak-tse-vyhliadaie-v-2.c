static void myeth_kick(struct myeth *priv, struct tx_desc *desc,
                       dma_addr_t desc_dma, dma_addr_t buf_dma, u32 len)
{
        desc->addr  = cpu_to_le64(buf_dma);
        desc->len   = cpu_to_le32(len);
        desc->flags = cpu_to_le32(DESC_OWN);   /* прапорець власності — останнім */

        writel(lower_32_bits(desc_dma), priv->regs + REG_TXDESC_LO);
        writel(upper_32_bits(desc_dma), priv->regs + REG_TXDESC_HI);
        writel(TX_KICK_GO, priv->regs + REG_TX_KICK);
}
