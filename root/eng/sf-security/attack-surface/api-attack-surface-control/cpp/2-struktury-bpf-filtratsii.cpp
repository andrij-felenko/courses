#include <linux/filter.h>
#include <linux/seccomp.h>
#include <cstdint>
#include <span>

namespace seccomp_api {

struct SockFilter {
    uint16_t code{0};
    uint8_t  jt{0};
    uint8_t  jf{0};
    uint32_t k{0};
};

struct SockFilterProgram {
    uint16_t len{0};
    const SockFilter* filter{nullptr};

    explicit SockFilterProgram(std::span<const SockFilter> instructions) noexcept
        : len{static_cast<uint16_t>(instructions.size())},
          filter{instructions.data()} {}
};

struct SeccompData {
    int32_t  nr{0};
    uint32_t arch{0};
    uint64_t instruction_pointer{0};
    uint64_t args[6]{0, 0, 0, 0, 0, 0};
};

} // namespace seccomp_api
