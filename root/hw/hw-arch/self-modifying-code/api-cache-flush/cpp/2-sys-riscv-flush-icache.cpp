#include <unistd.h>
#include <sys/syscall.h>
#include <span>
#include <expected>
#include <system_error>

#define SYS_riscv_flush_icache __NR_riscv_flush_icache
enum class RiscvFlushScope : uintptr_t {
    AllCores = 0UL,
    LocalCoreOnly = 1UL
};

inline std::expected<void, std::error_code> riscv_flush_icache(
    std::span<const uint8_t> code, RiscvFlushScope scope) noexcept {
    uintptr_t start = reinterpret_cast<uintptr_t>(code.data());
    uintptr_t end = start + code.size();
    long ret = syscall(SYS_riscv_flush_icache, start, end, static_cast<uintptr_t>(scope));
    if (ret != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
