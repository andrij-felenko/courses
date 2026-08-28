#pragma once

#include "vector_table_types.h"

namespace vtm::hardware {

class mpu_controller {
public:
    static status initialize_protection(uintptr_t base_address, std::size_t size_bytes) noexcept {
        if ((base_address % vector_table_alignment) != 0) {
            return status::error_alignment;
        }

        if (size_bytes > vector_table_alignment) {
            return status::error_mpu_config;
        }

        auto* const mpu_type = reinterpret_cast<volatile uint32_t*>(0xE000ED90);
        auto* const mpu_ctrl = reinterpret_cast<volatile uint32_t*>(0xE000ED94);
        auto* const mpu_rnr  = reinterpret_cast<volatile uint32_t*>(0xE000ED98);
        auto* const mpu_rbar = reinterpret_cast<volatile uint32_t*>(0xE000ED9C);
        auto* const mpu_rasr = reinterpret_cast<volatile uint32_t*>(0xE000EDA0);

        if ((*mpu_type & 0xFF00) == 0) {
            return status::error_mpu_config;
        }

        *mpu_ctrl = 0;
        asm volatile ("dsb 0xF" : : : "memory");

        *mpu_rnr = mpu_region_number;
        *mpu_rbar = base_address & ~0x1FUL;

        // XN = 1, AP = 0b110 (Privileged RO), Size = 1024B, Enable = 1
        const uint32_t rasr_val = (1UL << 28) | (6UL << 24) | (1UL << 19) | (9UL << 1) | (1UL << 0);
        *mpu_rasr = rasr_val;

        *mpu_ctrl = (1UL << 2) | (1UL << 0); // PRIVDEFENA | ENABLE
        asm volatile ("dsb 0xF\n isb 0xF" : : : "memory");

        return status::ok;
    }

    class scoped_write_lock {
    public:
        scoped_write_lock() noexcept {
            auto* const mpu_rnr  = reinterpret_cast<volatile uint32_t*>(0xE000ED98);
            auto* const mpu_rasr = reinterpret_cast<volatile uint32_t*>(0xE000EDA0);
            *mpu_rnr = mpu_region_number;
            uint32_t val = *mpu_rasr;
            val &= ~(7UL << 24);
            val |= (1UL << 24); // Privileged Read-Write
            *mpu_rasr = val;
            asm volatile ("dsb 0xF\n isb 0xF" : : : "memory");
        }

        ~scoped_write_lock() noexcept {
            auto* const mpu_rnr  = reinterpret_cast<volatile uint32_t*>(0xE000ED98);
            auto* const mpu_rasr = reinterpret_cast<volatile uint32_t*>(0xE000EDA0);
            *mpu_rnr = mpu_region_number;
            uint32_t val = *mpu_rasr;
            val &= ~(7UL << 24);
            val |= (6UL << 24); // Privileged Read-Only
            *mpu_rasr = val;
            asm volatile ("dsb 0xF\n isb 0xF" : : : "memory");
        }

        scoped_write_lock(const scoped_write_lock&) = delete;
        scoped_write_lock& operator=(const scoped_write_lock&) = delete;
        scoped_write_lock(scoped_write_lock&&) = delete;
        scoped_write_lock& operator=(scoped_write_lock&&) = delete;
    };
};

} // namespace vtm::hardware
