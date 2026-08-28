// Повільний шлях (Slow Path) — виконується лише під час промахів або MMIO
uint32_t softtlb_slow_read32(CPUState *env, uint32_t gva) {
    uint32_t page_addr = gva & PAGE_MASK;
    uint32_t gpa;
    
    // Перевірка на перетин межі сторінки (Split Page Access)
    if ((gva & ~PAGE_MASK) > (PAGE_SIZE - 4)) {
        // Читання перетинає межу двох сторінок — зчитуємо по байтах
        uint8_t b0 = softtlb_slow_read8(env, gva + 0);
        uint8_t b1 = softtlb_slow_read8(env, gva + 1);
        uint8_t b2 = softtlb_slow_read8(env, gva + 2);
        uint8_t b3 = softtlb_slow_read8(env, gva + 3);
        return b0 | (b1 << 8) | (b2 << 16) | (b3 << 24);
    }
    
    // 1. Прохід гостьових таблиць сторінок MMU
    if (!guest_mmu_translate(env, page_addr, &gpa, ACCESS_READ)) {
        // Сторінка відсутня або немає прав — генеруємо гостьовий Page Fault!
        raise_guest_exception(env, EXCP_PAGE_FAULT, gva);
        return 0;
    }
    
    // 2. Перевірка: чи це фізична RAM, чи апаратний регістр пристрою (MMIO)
    if (is_mmio_address(gpa)) {
        return mmio_device_read(gpa, 4);
    }
    
    // 3. Сторінка в RAM — вираховуємо відповідну адресу хоста
    uint8_t *host_ptr = get_host_ram_pointer(gpa);
    uint32_t index = (gva >> PAGE_SHIFT) & (SOFTTLB_SIZE - 1);
    
    // 4. Оновлюємо запис у SoftTLB для наступних миттєвих звернень
    env->mmu.tlb_read[index].tag_vaddr = page_addr;
    env->mmu.tlb_read[index].addend    = (uintptr_t)host_ptr - page_addr;
    
    // 5. Повертаємо прочитане значення
    return *(const uint32_t *)(host_ptr + (gva & ~PAGE_MASK));
}
