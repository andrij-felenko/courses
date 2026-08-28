#include <cstdint>
#include <linux/vfio.h>

namespace vfio::api {
    using RegionInfo = ::vfio_region_info;

    constexpr RegionInfo make_region_info(uint32_t index) noexcept {
        return RegionInfo{
            .argsz = sizeof(RegionInfo),
            .flags = 0,
            .index = index,
            .cap_offset = 0,
            .size = 0,
            .offset = 0
        };
    }
}
