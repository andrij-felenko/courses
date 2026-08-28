#pragma once

#include "vector_table_types.h"

namespace vtm::hardware {

class cache_synchronizer {
public:
    static constexpr std::size_t cache_line_size = 32;

    static void flush_data_and_invalidate_instruction(uintptr_t start_address, std::size_t length) noexcept {
        auto* const dccmvac = reinterpret_cast<volatile uint32_t*>(0xE000EF68);
        auto* const iciallu = reinterpret_cast<volatile uint32_t*>(0xE000EF50);

        uintptr_t current = start_address & ~(cache_line_size - 1);
        const uintptr_t end = start_address + length;

        while (current < end) {
            *dccmvac = current;
            current += cache_line_size;
        }
        asm volatile ("dsb 0xF" : : : "memory");

        *iciallu = 0;
        asm volatile ("dsb 0xF\n isb 0xF" : : : "memory");
    }
};

} // namespace vtm::hardware
