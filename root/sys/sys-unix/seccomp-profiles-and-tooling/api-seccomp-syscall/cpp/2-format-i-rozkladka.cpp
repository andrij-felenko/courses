#include <linux/seccomp.h>
#include <cstdint>
#include <span>

namespace sys {

// Структурне представлення аргументів виклику для безпечного обходу у C++
struct SeccompDataView {
    int32_t nr;
    uint32_t arch;
    uint64_t ip;
    std::span<const uint64_t, 6> args;

    explicit SeccompDataView(const ::seccomp_data& raw) noexcept
        : nr(raw.nr), arch(raw.arch), ip(raw.instruction_pointer), args(raw.args) {}
};

} // namespace sys
