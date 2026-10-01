#include <stdint.h>

#define SPI_INT_ST_REG             (0x60000E00 + 0x20)
#define SPI_INT_CLR_REG            (0x60000E00 + 0x24)
#define SPI_DMA_IN_SUC_EOF_INT_ST  (1 << 5)
#define SPI_DMA_IN_SUC_EOF_INT_CLR (1 << 5)

void hspi_dma_eof_isr(lldesc_t *desc) {
    volatile uint32_t *int_st  = (volatile uint32_t *)SPI_INT_ST_REG;
    volatile uint32_t *int_clr = (volatile uint32_t *)SPI_INT_CLR_REG;

    if (*int_st & SPI_DMA_IN_SUC_EOF_INT_ST) {
        *int_clr = SPI_DMA_IN_SUC_EOF_INT_CLR;
        if (desc && desc->owner == 0) {
            // Читання або оновлення буфера в пам'яті
            desc->owner = 1; // Передача буфера назад DMA
        }
    }
}
