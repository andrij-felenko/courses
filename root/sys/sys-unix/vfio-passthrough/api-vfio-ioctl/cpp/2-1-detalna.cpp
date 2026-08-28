#include <cstdint>
#include <linux/vfio.h>

// У C++20 ту саму структуру ядра заповнюють призначеними ініціалізаторами
namespace vfio::api {
    using DmaMapRequest = ::vfio_iommu_type1_dma_map;

    constexpr DmaMapRequest make_dma_map(uint64_t hva, uint64_t iova, uint64_t size, uint32_t flags) noexcept {
        return DmaMapRequest{
            .argsz = sizeof(DmaMapRequest),
            .flags = flags,
            .vaddr = hva,
            .iova = iova,
            .size = size
        };
    }
}
