/* Налаштування апаратного блітера DMA2D для копіювання спрайту з QSPI Flash (C) */
void draw_bitmap_from_qspi(uint32_t flash_addr, uint32_t fb_addr, uint16_t w, uint16_t h) {
    DMA2D->CR = (0U << DMA2D_CR_MODE_Pos); // Memory-to-Memory transfer
    DMA2D->OPFCCR = DMA2D_OUTPUT_RGB565;   // Формат виходу

    DMA2D->FGMAR = flash_addr;             // Джерело: 0x90xxxxxx (QSPI Flash)
    DMA2D->OMAR  = fb_addr;                // Призначення: 0xC0xxxxxx (SDRAM Framebuffer)
    
    DMA2D->FGOR  = 0;                      // Зсув рядка джерела
    DMA2D->OOR   = 800 - w;                // Зсув рядка екрана (800x480)

    DMA2D->NLR   = (w << DMA2D_NLR_PL_Pos) | (h << DMA2D_NLR_NL_Pos);
    DMA2D->CR   |= DMA2D_CR_START;         // Апаратний старт передачі
}
