#include <cstdint>

constexpr uintptr_t REG_SPI_BASE         = 0x60000E00;
constexpr uintptr_t SPI_DMA_CONF_REG     = REG_SPI_BASE + 0x84;
constexpr uintptr_t SPI_DMA_OUT_LINK_REG = REG_SPI_BASE + 0x88;

constexpr uint32_t SPI_AHBM_RST          = 1U << 16;
constexpr uint32_t SPI_AHBM_FIFO_RST     = 1U << 17;
constexpr uint32_t SPI_DMA_OUTLINK_START = 1U << 29;

class HspiDmaRing {
public:
    static void init(lldesc_t& d1, lldesc_t& d2, uint8_t* buf1, uint8_t* buf2, uint16_t len) {
        d1.length = len;
        d1.size = len;
        d1.sub_sof = 0;
        d1.reserved = 0;
        d1.eof = 0;
        d1.owner = 1;
        d1.buf = buf1;
        d1.next_link = &d2;

        d2.length = len;
        d2.size = len;
        d2.sub_sof = 0;
        d2.reserved = 0;
        d2.eof = 0;
        d2.owner = 1;
        d2.buf = buf2;
        d2.next_link = &d1;

        auto* conf = reinterpret_cast<volatile uint32_t*>(SPI_DMA_CONF_REG);
        *conf |= (SPI_AHBM_RST | SPI_AHBM_FIFO_RST);
        *conf &= ~(SPI_AHBM_RST | SPI_AHBM_FIFO_RST);

        auto* out_link = reinterpret_cast<volatile uint32_t*>(SPI_DMA_OUT_LINK_REG);
        *out_link = (reinterpret_cast<uintptr_t>(&d1) & 0xFFFFF) | SPI_DMA_OUTLINK_START;
    }
};
