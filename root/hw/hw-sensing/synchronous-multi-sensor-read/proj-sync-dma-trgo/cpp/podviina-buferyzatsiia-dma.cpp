namespace hardware {

class DoubleBufferedDma {
public:
    static void configure(DMA_Stream_TypeDef* stream, SPI_TypeDef* spi,
                          std::span<std::uint8_t> buf0,
                          std::span<std::uint8_t> buf1) noexcept {
        stream->CR &= ~DMA_SxCR_EN;
        while (stream->CR & DMA_SxCR_EN) {}

        stream->PAR = reinterpret_cast<std::uint32_t>(&(spi->DR));
        stream->M0AR = reinterpret_cast<std::uint32_t>(buf0.data());
        stream->M1AR = reinterpret_cast<std::uint32_t>(buf1.data());
        stream->NDTR = static_cast<std::uint16_t>(buf0.size());

        stream->CR |= DMA_SxCR_DBM | DMA_SxCR_MINC | DMA_SxCR_TCIE;
        stream->CR |= DMA_SxCR_EN;
    }

    [[nodiscard]] static std::uint8_t get_current_target(const DMA_Stream_TypeDef* stream) noexcept {
        return (stream->CR & DMA_SxCR_CT) ? 1 : 0;
    }
};

} // namespace hardware
