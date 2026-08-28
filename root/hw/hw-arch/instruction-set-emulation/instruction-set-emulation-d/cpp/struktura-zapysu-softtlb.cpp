constexpr size_t SoftTLBSize = 512;
constexpr size_t PageShift   = 12;
constexpr size_t PageSize    = 1ULL << PageShift; // 4 КіБ
constexpr size_t PageMask    = ~(PageSize - 1);

struct SoftTLBEntry {
    uint32_t  tag_vaddr{0xFFFFFFFF}; // Невалідний початковий тег
    uintptr_t addend{0};             // HVA = GVA + addend
};

struct CPUMMUState {
    std::array<SoftTLBEntry, SoftTLBSize> tlb_read{};
    std::array<SoftTLBEntry, SoftTLBSize> tlb_write{};
};
