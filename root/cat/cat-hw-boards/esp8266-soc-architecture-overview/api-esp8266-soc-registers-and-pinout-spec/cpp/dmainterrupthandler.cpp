#include <cstdint>

constexpr uintptr_t SPI_INT_ST_REG             = 0x60000E20;
constexpr uintptr_t SPI_INT_CLR_REG            = 0x60000E24;
constexpr uint32_t SPI_DMA_IN_SUC_EOF_INT_ST  = 1U << 5;
constexpr uint32_t SPI_DMA_IN_SUC_EOF_INT_CLR = 1U << 5;

class DmaInterruptHandler {
public:
    static void handle_eof_isr(lldesc_t* desc) {
        auto* int_st  = reinterpret_cast<volatile uint32_t*>(SPI_INT_ST_REG);
        auto* int_clr = reinterpret_cast<volatile uint32_t*>(SPI_INT_CLR_REG);

        if (*int_st & SPI_DMA_IN_SUC_EOF_INT_ST) {
            *int_clr = SPI_DMA_IN_SUC_EOF_INT_CLR;
            if (desc && desc->owner == 0) {
                // Обробка буфера процесором
                desc->owner = 1;
            }
        }
    }
};
