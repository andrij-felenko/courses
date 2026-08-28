#include <cstdint>
#include <linux/vfio.h>

namespace vfio::api {
    using GroupStatus = ::vfio_group_status;

    constexpr GroupStatus make_group_status() noexcept {
        return GroupStatus{
            .argsz = sizeof(GroupStatus),
            .flags = 0
        };
    }
}
