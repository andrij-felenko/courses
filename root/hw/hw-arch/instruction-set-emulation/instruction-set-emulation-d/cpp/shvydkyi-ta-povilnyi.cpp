uint32_t softtlb_slow_read32(CPUState& env, uint32_t gva) {
    uint32_t page_addr = gva & PageMask;
    uint32_t gpa{0};
    
    // Перевірка на перетин межі сторінки (Split Page Access)
    if ((gva & ~PageMask) > (PageSize - 4)) {
        uint8_t b0 = softtlb_slow_read8(env, gva + 0);
        uint8_t b1 = softtlb_slow_read8(env, gva + 1);
        uint8_t b2 = softtlb_slow_read8(env, gva + 2);
        uint8_t b3 = softtlb_slow_read8(env, gva + 3);
        return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24);
    }
    
    // 1. Прохід гостьових таблиць MMU
    if (!guest_mmu_translate(env, page_addr, gpa, AccessType::Read)) {
        raise_guest_exception(env, ExceptionCode::PageFault, gva);
        return 0;
    }
    
    // 2. Перевірка на MMIO
    if (is_mmio_address(gpa)) {
        return mmio_device_read(gpa, 4);
    }
    
    // 3. Оновлення SoftTLB
    uint8_t* host_ptr = get_host_ram_pointer(gpa);
    size_t index = (gva >> PageShift) & (SoftTLBSize - 1);
    
    env.mmu.tlb_read[index].tag_vaddr = page_addr;
    env.mmu.tlb_read[index].addend    = reinterpret_cast<uintptr_t>(host_ptr) - page_addr;
    
    return *reinterpret_cast<const uint32_t*>(host_ptr + (gva & ~PageMask));
}
