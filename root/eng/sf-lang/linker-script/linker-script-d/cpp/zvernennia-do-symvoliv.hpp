// Отримання адрес символів лінкера мовою C++20
#include <cstdint>
#include <span>
#include <concepts>

// Експорт символів із лінкер-скрипта через масиви
extern "C" {
    extern std::uint32_t _sdata[];
    extern std::uint32_t _edata[];
    extern std::uint32_t _sbss[];
    extern std::uint32_t _ebss[];
}

struct MemorySectionInfo {
    std::uintptr_t start_address;
    std::uintptr_t end_address;
    std::size_t size_bytes;
};

MemorySectionInfo get_data_section_info() noexcept {
    const auto start = reinterpret_cast<std::uintptr_t>(_sdata);
    const auto end   = reinterpret_cast<std::uintptr_t>(_edata);
    return {
        .start_address = start,
        .end_address   = end,
        .size_bytes    = end - start
    };
}

MemorySectionInfo get_bss_section_info() noexcept {
    const auto start = reinterpret_cast<std::uintptr_t>(_sbss);
    const auto end   = reinterpret_cast<std::uintptr_t>(_ebss);
    return {
        .start_address = start,
        .end_address   = end,
        .size_bytes    = end - start
    };
}
