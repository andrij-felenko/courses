#include <numaif.h>
#include <expected>
#include <system_error>

struct MemoryPolicyInfo {
    int mode{0};
    unsigned long nodemask{0};
};

std::expected<MemoryPolicyInfo, std::error_code> query_address_policy(
    const void* addr, unsigned long flags = 0) noexcept;
