#define SOFTTLB_SIZE 512
#define PAGE_SHIFT   12
#define PAGE_SIZE    (1UL << PAGE_SHIFT) // 4096 байтів
#define PAGE_MASK    (~(PAGE_SIZE - 1))

typedef struct SoftTLBEntry {
    uint32_t tag_vaddr;     // Тег віртуальної сторінки (GVA & PAGE_MASK)
    uintptr_t addend;       // Зміщення для отримання адреси хоста: HVA = GVA + addend
} SoftTLBEntry;

typedef struct CPUMMUState {
    SoftTLBEntry tlb_read[SOFTTLB_SIZE];
    SoftTLBEntry tlb_write[SOFTTLB_SIZE];
} CPUMMUState;
