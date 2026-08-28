#include <unistd.h>
#include <cerrno>
#include <cstddef>
#include <span>
#include <expected>
#include <system_error>
#include <type_traits>

// Узагальнена обгортка над довільним системним викликом із захистом від EINTR
template <typename Syscall, typename... Args>
auto retry_on_eintr(Syscall&& call, Args&&... args) 
    -> std::invoke_result_t<Syscall, Args...> 
{
    using ResultType = std::invoke_result_t<Syscall, Args...>;
    ResultType res;
    do {
        res = call(std::forward<Args>(args)...);
    } while (res == static_cast<ResultType>(-1) && errno == EINTR);
    return res;
}

// Повне надійне читання з типізованим результатом
std::expected<std::size_t, std::error_code> read_exact(int fd, std::span<char> buf) {
    std::size_t total = 0;
    while (total < buf.size()) {
        ssize_t res = retry_on_eintr(::read, fd, buf.data() + total, buf.size() - total);
        if (res == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        if (res == 0) {
            break; // EOF
        }
        total += static_cast<std::size_t>(res);
    }
    return total;
}

// Повний надійний запис
std::expected<std::size_t, std::error_code> write_exact(int fd, std::span<const char> buf) {
    std::size_t total = 0;
    while (total < buf.size()) {
        ssize_t res = retry_on_eintr(::write, fd, buf.data() + total, buf.size() - total);
        if (res == -1) {
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        if (res == 0) {
            break;
        }
        total += static_cast<std::size_t>(res);
    }
    return total;
}
