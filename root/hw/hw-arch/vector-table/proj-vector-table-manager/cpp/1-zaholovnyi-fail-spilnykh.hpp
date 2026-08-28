#pragma once

#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <expected>
#include <optional>
#include <string_view>

namespace vtm {

constexpr std::size_t sys_exceptions_count = 16;
constexpr std::size_t max_irq_count = 128;
constexpr std::size_t total_vector_slots = sys_exceptions_count + max_irq_count;
constexpr std::size_t vector_table_alignment = 1024;
constexpr uint32_t mpu_region_number = 7;

using isr_fn = void (*)() noexcept;

template <typename F>
concept IsrCallback = std::is_invocable_r_v<void, F>;

enum class status : uint8_t {
    ok = 0,
    error_not_initialized,
    error_already_initialized,
    error_null_ptr,
    error_alignment,
    error_invalid_irq_num,
    error_invalid_thumb_bit,
    error_mpu_config,
    error_bus_fault
};

[[nodiscard]] constexpr std::string_view to_string(status st) noexcept {
    switch (st) {
        case status::ok: return "OK";
        case status::error_not_initialized: return "Not Initialized";
        case status::error_already_initialized: return "Already Initialized";
        case status::error_null_ptr: return "Null Pointer";
        case status::error_alignment: return "Alignment Error";
        case status::error_invalid_irq_num: return "Invalid IRQ Number";
        case status::error_invalid_thumb_bit: return "Invalid Thumb Bit";
        case status::error_mpu_config: return "MPU Configuration Error";
        case status::error_bus_fault: return "Bus Fault";
        default: return "Unknown Error";
    }
}

struct alignas(4) exception_frame {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t psr;
};

struct crash_report {
    exception_frame frame;
    uintptr_t exc_return;
    uint32_t hfsr;
    uint32_t cfsr;
    uint32_t bfar;
    uint32_t mmar;
    uint32_t afsr;
    bool bfar_valid;
    bool mmar_valid;
    bool used_psp;
    uint32_t timestamp;
};

} // namespace vtm
