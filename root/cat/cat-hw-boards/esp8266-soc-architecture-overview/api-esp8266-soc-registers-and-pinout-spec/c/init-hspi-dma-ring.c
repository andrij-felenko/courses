#include <stdint.h>

#define REG_SPI_BASE         0x60000E00
#define SPI_DMA_CONF_REG     (REG_SPI_BASE + 0x84)
#define SPI_DMA_OUT_LINK_REG (REG_SPI_BASE + 0x88)

#define SPI_AHBM_RST          (1 << 16)
#define SPI_AHBM_FIFO_RST     (1 << 17)
#define SPI_DMA_OUTLINK_START (1 << 29)

static lldesc_t d1, d2;
static uint8_t buf1[512], buf2[512];

void init_hspi_dma_ring(void) {
    d1.length = 512;
    d1.size = 512;
    d1.sub_sof = 0;
    d1.reserved = 0;
    d1.eof = 0;
    d1.owner = 1;
    d1.buf = buf1;
    d1.next_link = &d2;

    d2.length = 512;
    d2.size = 512;
    d2.sub_sof = 0;
    d2.reserved = 0;
    d2.eof = 0;
    d2.owner = 1;
    d2.buf = buf2;
    d2.next_link = &d1;

    volatile uint32_t *conf_reg = (volatile uint32_t *)SPI_DMA_CONF_REG;
    *conf_reg |= (SPI_AHBM_RST | SPI_AHBM_FIFO_RST);
    *conf_reg &= ~(SPI_AHBM_RST | SPI_AHBM_FIFO_RST);

    volatile uint32_t *out_link_reg = (volatile uint32_t *)SPI_DMA_OUT_LINK_REG;
    *out_link_reg = (((uint32_t)&d1) & 0xFFFFF) | SPI_DMA_OUTLINK_START;
}
