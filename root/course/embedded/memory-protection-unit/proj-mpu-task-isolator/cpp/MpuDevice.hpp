#ifndef MPU_DEVICE_HPP
#define MPU_DEVICE_HPP

#include "MpuTypes.hpp"

namespace embedded::mpu {

class MpuDevice {
public:
    explicit MpuDevice(Architecture arch) noexcept : arch_(arch) {}

    [[nodiscard]] std::expected<void, ConfigError> initialize(bool enable_background_map) noexcept;
    [[nodiscard]] std::expected<void, ConfigError> program_region(const MemoryRegion& region) noexcept;
    [[nodiscard]] std::expected<void, ConfigError> disable_region(uint8_t index) noexcept;

    void fast_switch_task_regions(const MemoryRegion& stack_region,
                                  const MemoryRegion& guard_region,
                                  const MemoryRegion* private_data_region) noexcept;

    [[nodiscard]] Architecture architecture() const noexcept { return arch_; }
    [[nodiscard]] uint32_t region_count() const noexcept { return total_regions_; }

    static void memory_barrier() noexcept;
    static void instruction_barrier() noexcept;

private:
    Architecture arch_;
    uint32_t     total_regions_{0};
    bool         initialized_{false};

    [[nodiscard]] static constexpr uint32_t encode_pmsav7_size(size_t size) noexcept;
    void setup_mair_attributes() noexcept;
};

} // namespace embedded::mpu

#endif // MPU_DEVICE_HPP
