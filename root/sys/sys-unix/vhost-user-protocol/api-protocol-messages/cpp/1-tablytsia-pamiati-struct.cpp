#include <cstdint>
#include <array>

struct VhostUserMemoryRegion {
    uint64_t guest_phys_addr{0};  // Базова адреса в пам'яті гостя (GPA)
    uint64_t memory_size{0};      // Розмір регіону в байтах
    uint64_t userspace_addr{0};   // Віртуальна адреса в QEMU (QEMU HVA)
    uint64_t mmap_offset{0};      // Зміщення від початку файлу
};

struct VhostUserMemory {
    uint32_t nregions{0};         // Кількість регіонів
    uint32_t padding{0};
    std::array<VhostUserMemoryRegion, 8> regions{};
};
