#include <seccomp.h>
#include <unistd.h>
#include <expected>
#include <system_error>
#include <memory>

namespace security {

struct SeccompDeleter {
    void operator()(scmp_filter_ctx ctx) const noexcept {
        if (ctx) {
            ::seccomp_release(ctx);
        }
    }
};

using UniqueSeccompCtx = std::unique_ptr<void, SeccompDeleter>;

[[nodiscard]] auto apply_strict_sandbox() noexcept -> std::expected<void, std::error_code> {
    // 1. Ініціалізація контексту: дія за замовчуванням — знищення процесу (KILL)
    UniqueSeccompCtx ctx(::seccomp_init(SCMP_ACT_KILL));
    if (!ctx) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 2. Явний білий список дозволених операцій
    const int allowed_syscalls[] = {
        SCMP_SYS(read),
        SCMP_SYS(write),
        SCMP_SYS(exit_group),
        SCMP_SYS(futex)
    };

    for (int sys_nr : allowed_syscalls) {
        if (::seccomp_rule_add(ctx.get(), SCMP_ACT_ALLOW, sys_nr, 0) < 0) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
    }

    // 3. Завантаження фільтра в ядро
    if (::seccomp_load(ctx.get()) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    return {};
}

} // namespace security
