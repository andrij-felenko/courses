#include <iostream>
#include <memory>
#include <seccomp.h>
#include <unistd.h>

namespace sandbox {

struct SeccompDeleter {
    void operator()(scmp_filter_ctx ctx) const noexcept {
        if (ctx) seccomp_release(ctx);
    }
};

using ScmpContext = std::unique_ptr<void, SeccompDeleter>;

bool apply_libseccomp_policy_cpp() {
    ScmpContext ctx(seccomp_init(SCMP_ACT_KILL_PROCESS));
    if (!ctx) return false;

    const int allowed[] = { SCMP_SYS(read), SCMP_SYS(write), SCMP_SYS(exit_group) };
    for (int sys_nr : allowed) {
        if (seccomp_rule_add(ctx.get(), SCMP_ACT_ALLOW, sys_nr, 0) < 0) {
            return false;
        }
    }

    return seccomp_load(ctx.get()) >= 0;
}

} // namespace sandbox
