#pragma once

#include "vector_table_types.h"
#include <array>

namespace vtm {

class vector_manager {
public:
    static vector_manager& instance() noexcept {
        static vector_manager mgr;
        return mgr;
    }

    std::expected<void, status> initialize() noexcept {
        if (is_initialized_) {
            return std::unexpected(status::error_already_initialized);
        }

        const auto sram_base = reinterpret_cast<uintptr_t>(sram_table_.data());
        if ((sram_base % vector_table_alignment) != 0) {
            return std::unexpected(status::error_alignment);
        }

        auto* const scb_vtor = reinterpret_cast<volatile uint32_t*>(0xE000ED08);
        const auto* const src = reinterpret_cast<const isr_fn*>(static_cast<uintptr_t>(*scb_vtor));

        for (std::size_t i = 0; i < total_vector_slots; ++i) {
            sram_table_[i] = src[i];
            flash_backup_[i] = src[i];
        }

        hardware::cache_synchronizer::flush_data_and_invalidate_instruction(
            sram_base, sizeof(sram_table_));

        asm volatile ("cpsid i" : : : "memory");
        *scb_vtor = static_cast<uint32_t>(sram_base);
        asm volatile ("dsb 0xF\n isb 0xF" : : : "memory");
        asm volatile ("cpsie i" : : : "memory");

        const auto mpu_res = hardware::mpu_controller::initialize_protection(
            sram_base, sizeof(sram_table_));

        if (mpu_res != status::ok) {
            return std::unexpected(mpu_res);
        }

        is_initialized_ = true;
        return {};
    }

    std::expected<isr_fn, status> register_handler(int16_t irq_num, isr_fn handler) noexcept {
        if (!is_initialized_) {
            if (auto res = initialize(); !res) {
                return std::unexpected(res.error());
            }
        }

        if (handler == nullptr) {
            return std::unexpected(status::error_null_ptr);
        }

        if (irq_num < -14 || irq_num >= static_cast<int16_t>(max_irq_count)) {
            return std::unexpected(status::error_invalid_irq_num);
        }

        const auto addr = reinterpret_cast<uintptr_t>(handler);
        if ((addr & 1UL) == 0) {
            return std::unexpected(status::error_invalid_thumb_bit);
        }

        const std::size_t slot = static_cast<std::size_t>(irq_num + static_cast<int16_t>(sys_exceptions_count));
        isr_fn previous = sram_table_[slot];

        {
            asm volatile ("cpsid i" : : : "memory");
            hardware::mpu_controller::scoped_write_lock lock;
            sram_table_[slot] = handler;
            asm volatile ("cpsie i" : : : "memory");
        }

        hardware::cache_synchronizer::flush_data_and_invalidate_instruction(
            reinterpret_cast<uintptr_t>(&sram_table_[slot]), sizeof(isr_fn));

        return previous;
    }

    std::expected<void, status> unregister_handler(int16_t irq_num) noexcept {
        if (!is_initialized_) {
            return std::unexpected(status::error_not_initialized);
        }

        if (irq_num < -14 || irq_num >= static_cast<int16_t>(max_irq_count)) {
            return std::unexpected(status::error_invalid_irq_num);
        }

        const std::size_t slot = static_cast<std::size_t>(irq_num + static_cast<int16_t>(sys_exceptions_count));
        const isr_fn default_handler = flash_backup_[slot];

        {
            asm volatile ("cpsid i" : : : "memory");
            hardware::mpu_controller::scoped_write_lock lock;
            sram_table_[slot] = default_handler;
            asm volatile ("cpsie i" : : : "memory");
        }

        hardware::cache_synchronizer::flush_data_and_invalidate_instruction(
            reinterpret_cast<uintptr_t>(&sram_table_[slot]), sizeof(isr_fn));

        return {};
    }

    [[nodiscard]] bool is_active() const noexcept { return is_initialized_; }
    [[nodiscard]] uintptr_t get_table_address() const noexcept {
        return reinterpret_cast<uintptr_t>(sram_table_.data());
    }

private:
    vector_manager() = default;

    alignas(vector_table_alignment) std::array<isr_fn, total_vector_slots> sram_table_{};
    std::array<isr_fn, total_vector_slots> flash_backup_{};
    bool is_initialized_{false};
};

} // namespace vtm
