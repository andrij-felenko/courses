static void swiotlb_bounce(struct device *dev, phys_addr_t orig_addr,
                           phys_addr_t tlb_addr, size_t size,
                           enum dma_data_direction dir)
{
    void *vorg = phys_to_virt(orig_addr);
    void *vtlb = phys_to_virt(tlb_addr);

    if (dir == DMA_TO_DEVICE || dir == DMA_BIDIRECTIONAL)
        memcpy(vtlb, vorg, size);
    else
        memcpy(vorg, vtlb, size);
}
