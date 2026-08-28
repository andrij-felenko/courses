#include <cstdint>
#include <vector>
#include <span>

/* C++ представлення окремого листка CPUID */
struct alignas(8) CpuidEntry {
    std::uint32_t function{0};   // Номер листка (EAX)
    std::uint32_t index{0};      // Номер підлистка (ECX)
    std::uint32_t flags{0};      // Керуючі прапорці (KVM_CPUID_FLAG_*)
    std::uint32_t eax{0};        // Результат EAX
    std::uint32_t ebx{0};        // Результат EBX
    std::uint32_t ecx{0};        // Результат ECX
    std::uint32_t edx{0};        // Результат EDX
    std::uint32_t padding[3]{0}; // Вирівнювання
};

/* C++ безпечний контейнер таблиці CPUID */
struct CpuidTable {
    std::vector<CpuidEntry> entries;

    [[nodiscard]] std::size_t byte_size() const noexcept {
        return sizeof(std::uint32_t) * 2 + entries.size() * sizeof(CpuidEntry);
    }
};
