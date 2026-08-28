#include <cstdint>
#include <linux/vfio.h>

namespace vfio::api {
    using IrqSet = ::vfio_irq_set;

    constexpr IrqSet make_irq_set(uint32_t index, uint32_t start, uint32_t count, uint32_t flags) noexcept {
        return IrqSet{
            .argsz = sizeof(IrqSet) + count * sizeof(int),
            .flags = flags,
            .index = index,
            .start = start,
            .count = count
        };
    }
}
