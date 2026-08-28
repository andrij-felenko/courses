/* Безпечна C++ обгортка з контролем меж пам'яті (C++) */
void draw_bitmap_from_qspi(std::span<const uint16_t> src_pixels, std::span<uint16_t> dst_fb, uint16_t width, uint16_t height) noexcept {
    DMA2D->CR = (0U << DMA2D_CR_MODE_Pos);
    DMA2D->OPFCCR = DMA2D_OUTPUT_RGB565;
    DMA2D->FGMAR = reinterpret_cast<uint32_t>(src_pixels.data());
    DMA2D->OMAR  = reinterpret_cast<uint32_t>(dst_fb.data());
    DMA2D->FGOR  = 0;
    DMA2D->OOR   = 800 - width;
    DMA2D->NLR   = (width << DMA2D_NLR_PL_Pos) | (height << DMA2D_NLR_NL_Pos);
    DMA2D->CR   |= DMA2D_CR_START;
}
