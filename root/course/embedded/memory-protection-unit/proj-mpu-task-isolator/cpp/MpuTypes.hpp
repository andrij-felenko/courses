#ifndef MPU_TYPES_HPP
#define MPU_TYPES_HPP

#include <cstdint>
#include <cstddef>
#include <span>
#include <expected>
#include <concepts>
#include <string_view>

namespace embedded::mpu {

/* Архітектурні покоління */
enum class Architecture : uint8_t {
    PmsaV7, /* Cortex-M3 / M4 / M7 */
    PmsaV8  /* Cortex-M23 / M33 / M55 / M85 */
};

/* Права доступу AP (Access Permission) */
enum class AccessPermission : uint32_t {
    NoAccess           = 0x0U, /* Priv: No,   Unpriv: No */
    PrivRwUnprivNo     = 0x1U, /* Priv: RW,   Unpriv: No */
    PrivRwUnprivRo     = 0x2U, /* Priv: RW,   Unpriv: RO */
    PrivRwUnprivRw     = 0x3U, /* Priv: RW,   Unpriv: RW */
    PrivRoUnprivNo     = 0x5U, /* Priv: RO,   Unpriv: No */
    PrivRoUnprivRo     = 0x6U  /* Priv: RO,   Unpriv: RO */
};

/* Тип пам'яті та кешованість */
enum class MemoryAttribute : uint8_t {
    Device_nGnRnE,    /* Строгий порядок без буферизації (периферія) */
    Device_nGnRE,     /* Периферія з буферизацією раннього запису */
    NormalNonCacheable,/* Звичайна пам'ять без кешу (DMA буфери) */
    NormalWriteThrough,/* Звичайна пам'ять Write-Through */
    NormalWriteBack   /* Звичайна пам'ять Write-Back, Read/Write-Allocate */
};

/* Коди помилок конфігурації MPU */
enum class ConfigError : uint8_t {
    DeviceNotFound,
    InvalidRegionNumber,
    InvalidSizeNotPowerOfTwo,
    UnalignedBaseAddress,
    Unaligned32ByteBoundary,
    OverlapConflict,
    HardwareDisabled
};

/* Дескриптор регіону пам'яті */
struct MemoryRegion {
    uint8_t          region_index{0};
    uintptr_t        base_address{0};
    size_t           size_bytes{0};
    AccessPermission permission{AccessPermission::PrivRwUnprivRw};
    MemoryAttribute  attribute{MemoryAttribute::NormalWriteBack};
    bool             execute_never{true};
    uint8_t          subregion_mask{0}; /* Лише для PMSAv7 */

    [[nodiscard]] constexpr uintptr_t end_address() const noexcept {
        return base_address + size_bytes;
    }

    [[nodiscard]] constexpr bool contains(uintptr_t address) const noexcept {
        return (address >= base_address) && (address < end_address());
    }

    [[nodiscard]] constexpr bool contains_range(uintptr_t start, size_t len) const noexcept {
        const uintptr_t end = start + len;
        return (end >= start) && (start >= base_address) && (end <= end_address());
    }
};

/* Апаратний стек-фрейм під час винятку Cortex-M */
struct alignas(8) StackFrame {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r12;
    uint32_t lr;
    uint32_t pc;
    uint32_t xpsr;
};

/* Розшифрований звіт про порушення прав захисту */
struct FaultReport {
    uint8_t     mmfsr_flags{0};
    uintptr_t   fault_address{0};
    bool        address_valid{false};
    uintptr_t   instruction_pc{0};
    uintptr_t   return_address{0};
    uint32_t    psr_state{0};
    bool        occurred_in_unprivileged_thread{false};
    std::string_view reason_description{};
};

} // namespace embedded::mpu

#endif // MPU_TYPES_HPP
