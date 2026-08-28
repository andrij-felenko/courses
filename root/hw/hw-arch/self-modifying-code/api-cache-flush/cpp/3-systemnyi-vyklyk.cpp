#include <linux/membarrier.h>
#include <sys/syscall.h>
#include <expected>
#include <system_error>

inline std::expected<void, std::error_code> sync_all_cores_membarrier() noexcept {
    int ret = syscall(__NR_membarrier, MEMBARRIER_CMD_PRIVATE_EXPEDITED_SYNC_CORE, 0, 0);
    if (ret != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
