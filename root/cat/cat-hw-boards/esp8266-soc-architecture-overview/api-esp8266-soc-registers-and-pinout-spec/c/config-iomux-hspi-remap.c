#include <stdint.h>

#define REG_IOMUX_BASE            0x60000800
#define PERIPHS_IO_MUX_MTCK_U     (REG_IOMUX_BASE + 0x08) // GPIO13 / HSPI_MOSI
#define PERIPHS_IO_MUX_MTMS_U     (REG_IOMUX_BASE + 0x0C) // GPIO14 / HSPI_CLK

#define PERIPHS_IO_MUX_FUNC_MASK  (~(0x7 << 4))
#define PERIPHS_IO_MUX_FUNC_HSPI  (0x2 << 4)

void config_iomux_hspi_remap(void) {
    volatile uint32_t *reg_mtck = (volatile uint32_t *)PERIPHS_IO_MUX_MTCK_U;
    volatile uint32_t *reg_mtms = (volatile uint32_t *)PERIPHS_IO_MUX_MTMS_U;

    *reg_mtck = (*reg_mtck & PERIPHS_IO_MUX_FUNC_MASK) | PERIPHS_IO_MUX_FUNC_HSPI;
    *reg_mtms = (*reg_mtms & PERIPHS_IO_MUX_FUNC_MASK) | PERIPHS_IO_MUX_FUNC_HSPI;
}
