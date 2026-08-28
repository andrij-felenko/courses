// Спрощена модель того, що MMU робить у залізі щодоступу.
#define PAGE_BITS  12u                 // сторінка 4 КБ = 2^12
#define PAGE_SIZE  (1u << PAGE_BITS)
#define OFFS_MASK  (PAGE_SIZE - 1u)     // молодші 12 бітів

uint32_t translate(const uint32_t page_table[], uint32_t virt) {
    uint32_t page   = virt >> PAGE_BITS;      // старші біти — номер сторінки
    uint32_t offset = virt & OFFS_MASK;       // молодші — зсув
    uint32_t frame  = page_table[page];       // де ця сторінка фізично
    return (frame << PAGE_BITS) | offset;     // склеїти кадр і зсув
}
