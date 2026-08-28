#include <cstdint>
#include <span>
#include <optional>
#include <elf.h>

struct RawAuxvResult {
    std::uint64_t argc{0};
    const Elf64_auxv_t* auxv_head{nullptr};
};

class RawStackWalker {
public:
    static std::optional<RawAuxvResult> inspect(const std::uint64_t* raw_rsp) noexcept {
        if (!raw_rsp) return std::nullopt;

        const std::uint64_t argc = *raw_rsp;
        const std::uint64_t* argv = raw_rsp + 1;
        const std::uint64_t* envp = argv + argc + 1;

        const std::uint64_t* env_runner = envp;
        while (*env_runner != 0) {
            ++env_runner;
        }
        ++env_runner; // Зсув за NULL термінатор envp

        return RawAuxvResult{
            .argc = argc,
            .auxv_head = reinterpret_cast<const Elf64_auxv_t*>(env_runner)
        };
    }
};
