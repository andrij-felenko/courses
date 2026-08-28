#include <unistd.h>
#include <cerrno>
#include <cstddef>
#include <span>
#include <expected>
#include <system_error>

// В ідіоматичному C++ шаблон бере на себе повтор за викликом ядра
template <typename Fn, typename... Args>
auto retry_syscall(Fn&& fn, Args&&... args) -> std::invoke_result_t<Fn, Args...> {
    using Res = std::invoke_result_t<Fn, Args...>;
    Res res;
    do {
        res = fn(std::forward<Args>(args)...);
    } while (res == static_cast<Res>(-1) && errno == EINTR);
    return res;
}

std::expected<std::size_t, std::error_code> robust_read(int fd, std::span<char> buf) {
    ssize_t res = retry_syscall(::read, fd, buf.data(), buf.size());
    if (res == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return static_cast<std::size_t>(res);
}
