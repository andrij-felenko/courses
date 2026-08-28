// Протокол безпечного оновлення вектора в кешованій пам'яті RAM
class cache_coherency_manager {
public:
    static void update_vector(uint32_t irq_num, isr_fn handler) noexcept {
        // 1. Оновлення покажчика в таблиці
        sram_vector_table[16 + irq_num] = handler;

        // 2. Скидання лінії D-Cache
        auto* const addr = reinterpret_cast<uint32_t*>(&sram_vector_table[16 + irq_num]);
        SCB_CleanDCache_by_Addr(addr, sizeof(uint32_t));

        // 3. Знедійнення I-Cache
        SCB_InvalidateICache();

        // 4. Бар'єри пам'яті
        asm volatile ("dsb 0xF\n isb 0xF" : : : "memory");
    }
};
