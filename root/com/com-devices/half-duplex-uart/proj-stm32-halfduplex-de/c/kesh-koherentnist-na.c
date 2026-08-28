// Керування когерентністю D-Cache для буферів DMA (ARM Cortex-M7, C)
void dma_rx_cache_invalidate(uint8_t *buffer, size_t length) {
    // Вирівнювання адреси та розміру по межі кеш-рядка (32 байти)
    uint32_t addr = (uint32_t)buffer;
    SCB_InvalidateDCache_by_Addr((uint32_t*)addr, length);
}

void dma_tx_cache_clean(const uint8_t *buffer, size_t length) {
    uint32_t addr = (uint32_t)buffer;
    SCB_CleanDCache_by_Addr((uint32_t*)addr, length);
}
