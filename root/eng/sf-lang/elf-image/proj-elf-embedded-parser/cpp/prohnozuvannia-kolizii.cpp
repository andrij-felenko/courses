#include <cstdint>
#include <iostream>
#include <iomanip>

namespace memory {

struct SramBudget {
    std::uint32_t data_size;
    std::uint32_t bss_size;
    std::uint32_t min_stack_size;
    std::uint32_t min_heap_size;
    std::uint32_t sram_capacity_bytes;

    [[nodiscard]] bool is_safe() const noexcept {
        const auto static_usage = data_size + bss_size;
        const auto required_minimum = static_usage + min_stack_size + min_heap_size;

        if (required_minimum > sram_capacity_bytes) {
            std::cerr << "КРИТИЧНЕ ПЕРЕПОВНЕННЯ SRAM!\n"
                      << "  Статичні змінні (.data + .bss): " << static_usage << " B\n"
                      << "  Мінімальний стек + купа:        " << (min_stack_size + min_heap_size) << " B\n"
                      << "  Фізична ємність SRAM:           " << sram_capacity_bytes << " B\n";
            return false;
        }

        const auto free_margin = sram_capacity_bytes - required_minimum;
        const auto free_percentage = (static_cast<double>(free_margin) / sram_capacity_bytes) * 100.0;

        std::cout << "Запас вільної RAM: " << free_margin << " байтів (" 
                  << std::fixed << std::setprecision(1) << free_percentage << "%)\n";
        return true;
    }
};

} // namespace memory
