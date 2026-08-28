#include <iostream>
#include <memory>
#include <string>
#include <expected>
#include <vector>
#include <seccomp.h>
#include <unistd.h>

namespace sandbox {

struct SeccompDeleter {
    void operator()(scmp_filter_ctx ctx) const noexcept {
        if (ctx) {
            seccomp_release(ctx);
        }
    }
};

using ScmpContext = std::unique_ptr<void, SeccompDeleter>;

class LibSeccompSandbox {
public:
    static std::expected<void, std::string> apply_worker_policy() {
        scmp_filter_ctx raw_ctx = seccomp_init(SCMP_ACT_KILL_PROCESS);
        if (!raw_ctx) {
            return std::unexpected("seccomp_init failed");
        }
        ScmpContext ctx(raw_ctx);

        const std::vector<int> allowed_syscalls = {
            SCMP_SYS(read),
            SCMP_SYS(write),
            SCMP_SYS(brk),
            SCMP_SYS(mmap),
            SCMP_SYS(exit_group),
            SCMP_SYS(exit)
        };

        for (int sys_nr : allowed_syscalls) {
            if (seccomp_rule_add(ctx.get(), SCMP_ACT_ALLOW, sys_nr, 0) < 0) {
                return std::unexpected("Failed to add rule for syscall number: " + std::to_string(sys_nr));
            }
        }

        if (seccomp_load(ctx.get()) < 0) {
            return std::unexpected("seccomp_load failed to install filter");
        }

        return {};
    }
};

} // namespace sandbox

int main() {
    auto status = sandbox::LibSeccompSandbox::apply_worker_policy();
    if (!status) {
        std::cerr << "Помилка встановлення політики: " << status.error() << '\n';
        return 1;
    }
    std::cout << "libseccomp RAII пісочниця активована!\n";
    return 0;
}
