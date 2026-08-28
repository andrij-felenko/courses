#include <array>
#include <cstdint>
#include <span>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

namespace rtos::heap5 {

struct MemoryRegionDescriptor {
    std::uintptr_t start_address;
    std::size_t size_in_bytes;
};

template <std::size_t RegionCount>
class MultiRegionHeapManager {
public:
    explicit constexpr MultiRegionHeapManager(
        const std::array<MemoryRegionDescriptor, RegionCount>& descriptors) noexcept
    {
        for (std::size_t i = 0; i < RegionCount; ++i) {
            c_regions_[i].pucStartAddress = reinterpret_cast<uint8_t*>(descriptors[i].start_address);
            c_regions_[i].xSizeInBytes = descriptors[i].size_in_bytes;
        }
        // Фінальний маркер-сентинел
        c_regions_[RegionCount].pucStartAddress = nullptr;
        c_regions_[RegionCount].xSizeInBytes = 0;
    }

    void initialize_heap() const noexcept {
        vPortDefineHeapRegions(c_regions_.data());
    }

private:
    mutable std::array<HeapRegion_t, RegionCount + 1> c_regions_{};
};

} // namespace rtos::heap5
