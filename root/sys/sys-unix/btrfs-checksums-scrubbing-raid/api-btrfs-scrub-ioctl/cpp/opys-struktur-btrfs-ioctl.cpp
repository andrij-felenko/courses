// C++ аналог структури аргументів з ініціалізацією за замовчуванням
#include <cstdint>
#include <linux/btrfs.h>

namespace btrfs::api {

struct ScrubArgs {
    std::uint64_t devid{0};
    std::uint64_t start{0};
    std::uint64_t end{static_cast<std::uint64_t>(-1)};
    std::uint64_t flags{0};
    btrfs_scrub_progress progress{};
};

} // namespace btrfs::api
