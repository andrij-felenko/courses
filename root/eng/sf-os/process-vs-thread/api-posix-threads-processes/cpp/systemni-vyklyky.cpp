#include <system_error>
#include <span>
#include <string_view>
#include <expected>
#include <sys/types.h>
#include <unistd.h>
#include <sys/wait.h>

// Ідіоматичні C++ сигнатури системних викликів
namespace sys {
    std::expected<pid_t, std::error_code> fork_process() noexcept;
    std::expected<void, std::error_code> exec_program(
        std::string_view path,
        std::span<const std::string_view> args,
        std::span<const std::string_view> env) noexcept;
    std::expected<int, std::error_code> wait_process(pid_t pid, int options = 0) noexcept;
    [[noreturn]] void exit_process(int status) noexcept;
}
