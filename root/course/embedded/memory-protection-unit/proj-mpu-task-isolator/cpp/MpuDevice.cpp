#include "MpuDevice.hpp"

namespace embedded::mpu {

namespace {
    constexpr uintptr_t scs_base  = 0xE000E000UL;
    constexpr uintptr_t mpu_base  = scs_base + 0x0D90UL;
    constexpr uintptr_t scb_base  = scs_base + 0x0D00UL;

    inline volatile uint32_t& reg_type()  noexcept { return *reinterpret_cast<volatile uint32_t*>(mpu_base + 0x00UL); }
    inline volatile uint32_t& reg_ctrl()  noexcept { return *reinterpret_cast<volatile uint32_t*>(mpu_base + 0x04UL); }
    inline volatile uint32_t& reg_rnr()   noexcept { return *reinterpret_cast<volatile uint32_t*>(mpu_base + 0x08UL); }
    inline volatile uint32_t& reg_rbar()  noexcept { return *reinterpret_cast<volatile uint32_t*>(mpu_base + 0x0CUL); }
    inline volatile uint32_t& reg_rasr()  noexcept { return *reinterpret_cast<volatile uint32_t*>(mpu_base + 0x10UL); }
    inline volatile uint32_t& reg_rlar()  noexcept { return *reinterpret_cast<volatile uint32_t*>(mpu_base + 0x10UL); }
    inline volatile uint32_t& reg_mair0() noexcept { return *reinterpret_cast<volatile uint32_t*>(mpu_base + 0x30UL); }
    inline volatile uint32_t& reg_shcsr() noexcept { return *reinterpret_cast<volatile uint32_t*>(scb_base + 0x24UL); }
}

void MpuDevice::memory_barrier() noexcept {
#if defined(__GNUC__) || defined(__clang__)
    __asm volatile("dsb 0xF" ::: "memory");
#endif
}

void MpuDevice::instruction_barrier() noexcept {
#if defined(__GNUC__) || defined(__clang__)
    __asm volatile("isb 0xF" ::: "memory");
#endif
}

constexpr uint32_t MpuDevice::encode_pmsav7_size(size_t size) noexcept {
    if (size < 32) return 0;
    uint32_t field = 0;
    size_t temp = size;
    while ((temp & 1U) == 0U) {
        temp >>= 1U;
        field++;
    }
    return (temp == 1U) ? (field - 1U) : 0U;
}

void MpuDevice::setup_mair_attributes() noexcept {
    /*
     * Attr 0: Normal Write-Back Read/Write-Allocate (0xFF)
     * Attr 1: Device-nGnRnE (0x00)
     * Attr 2: Normal Non-cacheable (0x44)
     * Attr 3: Normal Write-Through (0xBB)
     */
    reg_mair0() = 0xBB4400FFUL;
}

std::expected<void, ConfigError> MpuDevice::initialize(bool enable_background_map) noexcept {
    const uint32_t type = reg_type();
    total_regions_ = (type >> 8) & 0xFFU;
    if (total_regions_ == 0) {
        return std::unexpected(ConfigError::DeviceNotFound);
    }

    /* Вимикаємо MPU перед налаштуванням */
    reg_ctrl() = 0U;
    memory_barrier();
    instruction_barrier();

    if (arch_ == Architecture::PmsaV8) {
        setup_mair_attributes();
    }

    /* Активація MemManage переривання в SCB */
    reg_shcsr() |= (1UL << 16);

    uint32_t ctrl = (1UL << 0) | (1UL << 1); /* ENABLE | HFNMIENA */
    if (enable_background_map) {
        ctrl |= (1UL << 2); /* PRIVDEFENA */
    }

    reg_ctrl() = ctrl;
    memory_barrier();
    instruction_barrier();

    initialized_ = true;
    return {};
}

std::expected<void, ConfigError> MpuDevice::program_region(const MemoryRegion& region) noexcept {
    if (region.region_index >= total_regions_) {
        return std::unexpected(ConfigError::InvalidRegionNumber);
    }

    reg_rnr() = region.region_index;

    if (arch_ == Architecture::PmsaV7) {
        const uint32_t size_field = encode_pmsav7_size(region.size_bytes);
        if (size_field == 0 && region.size_bytes != 0) {
            return std::unexpected(ConfigError::InvalidSizeNotPowerOfTwo);
        }
        if ((region.base_address & (region.size_bytes - 1U)) != 0U) {
            return std::unexpected(ConfigError::UnalignedBaseAddress);
        }

        reg_rbar() = (region.base_address & 0xFFFFFFE0UL);

        uint32_t rasr = 0;
        if (region.size_bytes > 0) {
            rasr |= 1UL; /* ENABLE */
            rasr |= (size_field << 1);
            rasr |= (static_cast<uint32_t>(region.subregion_mask) << 8);

            uint32_t tex = 0, c = 0, b = 0, s = 1;
            switch (region.attribute) {
                case MemoryAttribute::Device_nGnRnE:
                    tex = 0; c = 0; b = 0; s = 1; break;
                case MemoryAttribute::Device_nGnRE:
                    tex = 0; c = 0; b = 1; s = 1; break;
                case MemoryAttribute::NormalNonCacheable:
                    tex = 1; c = 0; b = 0; s = 1; break;
                case MemoryAttribute::NormalWriteThrough:
                    tex = 0; c = 1; b = 0; s = 0; break;
                case MemoryAttribute::NormalWriteBack:
                default:
                    tex = 1; c = 1; b = 1; s = 1; break;
            }

            rasr |= (b << 16) | (c << 17) | (s << 18) | (tex << 19);
            rasr |= (static_cast<uint32_t>(region.permission) << 24);
            if (region.execute_never) {
                rasr |= (1UL << 28);
            }
        }
        reg_rasr() = rasr;

    } else {
        if ((region.base_address & 0x1FUL) != 0U) {
            return std::unexpected(ConfigError::Unaligned32ByteBoundary);
        }

        const uintptr_t limit = region.base_address + region.size_bytes - 1U;
        uint32_t rbar = (region.base_address & 0xFFFFFFE0UL) | (0x02UL << 3);
        rbar |= (static_cast<uint32_t>(region.permission) << 1);
        if (region.execute_never) {
            rbar |= 1UL;
        }
        reg_rbar() = rbar;

        uint32_t attr_idx = 0;
        switch (region.attribute) {
            case MemoryAttribute::Device_nGnRnE:    attr_idx = 1; break;
            case MemoryAttribute::NormalNonCacheable:attr_idx = 2; break;
            case MemoryAttribute::NormalWriteThrough:attr_idx = 3; break;
            case MemoryAttribute::NormalWriteBack:
            default:                                 attr_idx = 0; break;
        }

        uint32_t rlar = (limit & 0xFFFFFFE0UL) | (attr_idx << 1);
        if (region.size_bytes > 0) {
            rlar |= 1UL;
        }
        reg_rlar() = rlar;
    }

    memory_barrier();
    instruction_barrier();
    return {};
}

std::expected<void, ConfigError> MpuDevice::disable_region(uint8_t index) noexcept {
    if (index >= total_regions_) {
        return std::unexpected(ConfigError::InvalidRegionNumber);
    }
    reg_rnr() = index;
    if (arch_ == Architecture::PmsaV7) {
        reg_rasr() = 0U;
    } else {
        reg_rlar() = 0U;
    }
    memory_barrier();
    instruction_barrier();
    return {};
}

void MpuDevice::fast_switch_task_regions(const MemoryRegion& stack_region,
                                         const MemoryRegion& guard_region,
                                         const MemoryRegion* private_data_region) noexcept {
    if (arch_ == Architecture::PmsaV7) {
        /* Регіон 5: Стек */
        const uint32_t stack_sz = encode_pmsav7_size(stack_region.size_bytes);
        reg_rbar() = (stack_region.base_address & 0xFFFFFFE0UL) | (1UL << 4) | 5U;
        reg_rasr() = 1UL | (stack_sz << 1) | (static_cast<uint32_t>(AccessPermission::PrivRwUnprivRw) << 24)
                   | (1UL << 28) | (1UL << 18) | (1UL << 19) | (1UL << 17) | (1UL << 16);

        /* Регіон 6: Захисна смуга стека (No Access) */
        const uint32_t guard_sz = encode_pmsav7_size(guard_region.size_bytes);
        reg_rbar() = (guard_region.base_address & 0xFFFFFFE0UL) | (1UL << 4) | 6U;
        reg_rasr() = 1UL | (guard_sz << 1) | (static_cast<uint32_t>(AccessPermission::NoAccess) << 24) | (1UL << 28);

        /* Регіон 7: Приватні дані */
        if (private_data_region && private_data_region->size_bytes > 0) {
            const uint32_t priv_sz = encode_pmsav7_size(private_data_region->size_bytes);
            reg_rbar() = (private_data_region->base_address & 0xFFFFFFE0UL) | (1UL << 4) | 7U;
            reg_rasr() = 1UL | (priv_sz << 1) | (static_cast<uint32_t>(AccessPermission::PrivRwUnprivRw) << 24)
                       | (1UL << 28) | (1UL << 18) | (1UL << 19) | (1UL << 17) | (1UL << 16);
        } else {
            reg_rbar() = (1UL << 4) | 7U;
            reg_rasr() = 0U;
        }
    } else {
        /* PMSAv8 */
        reg_rnr() = 5U;
        reg_rbar() = (stack_region.base_address & 0xFFFFFFE0UL) | (static_cast<uint32_t>(AccessPermission::PrivRwUnprivRw) << 1) | 1UL;
        reg_rlar() = ((stack_region.base_address + stack_region.size_bytes - 1U) & 0xFFFFFFE0UL) | 1UL;

        reg_rnr() = 6U;
        reg_rbar() = (guard_region.base_address & 0xFFFFFFE0UL) | (static_cast<uint32_t>(AccessPermission::NoAccess) << 1) | 1UL;
        reg_rlar() = ((guard_region.base_address + guard_region.size_bytes - 1U) & 0xFFFFFFE0UL) | 1UL;

        reg_rnr() = 7U;
        if (private_data_region && private_data_region->size_bytes > 0) {
            reg_rbar() = (private_data_region->base_address & 0xFFFFFFE0UL) | (static_cast<uint32_t>(AccessPermission::PrivRwUnprivRw) << 1) | 1UL;
            reg_rlar() = ((private_data_region->base_address + private_data_region->size_bytes - 1U) & 0xFFFFFFE0UL) | 1UL;
        } else {
            reg_rlar() = 0U;
        }
    }

    memory_barrier();
    instruction_barrier();
}

} // namespace embedded::mpu
