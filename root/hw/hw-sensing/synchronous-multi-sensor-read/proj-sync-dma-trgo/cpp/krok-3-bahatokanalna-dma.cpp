namespace hardware {

template <std::size_t BufferSize>
class DmaSpiReceiver {
public:
    static void configure(DMA_Stream_TypeDef* stream, SPI_TypeDef* spi, std::uint8_t* destination) noexcept {
        stream->CR = 0;
        while (stream->CR & DMA_SxCR_EN) {} // Очікування вимкнення

        stream->PAR = reinterpret_cast<std::uint32_t>(&(spi->DR));
        stream->M0AR = reinterpret_cast<std::uint32_t>(destination);
        stream->NDTR = BufferSize;
        stream->CR = DMA_SxCR_MINC | DMA_SxCR_TCIE;

        spi->CR2 |= SPI_CR2_RXDMAEN | SPI_CR2_TXDMAEN;
    }

    static void start_transfer(DMA_Stream_TypeDef* stream, std::size_t length) noexcept {
        stream->NDTR = length;
        stream->CR |= DMA_SxCR_EN;
    }
};

} // namespace hardware
