#include <linux/dma-mapping.h>

struct rx_desc { __le64 addr; __le32 len; __le32 status; };  /* формат заліза */

/* Кільце дескрипторів — обидва боки смикають його весь час → когерентний мапінг. */
ring->desc = dma_alloc_coherent(dev, RING_N * sizeof(struct rx_desc),
                                &ring->desc_dma, GFP_KERNEL);
if (!ring->desc)
    return -ENOMEM;
/* ring->desc     — адреса для ЯДРА (ним ядро пише дескриптори)
   ring->desc_dma — IOVA, яку віддаємо карті в регістр бази кільця        */
iowrite32(lower_32_bits(ring->desc_dma), regs + REG_RXRING_BASE_LO);
iowrite32(upper_32_bits(ring->desc_dma), regs + REG_RXRING_BASE_HI);
