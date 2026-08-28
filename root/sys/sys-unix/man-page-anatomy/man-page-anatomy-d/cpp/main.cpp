#include <unistd.h>
#include <cerrno>
#include <system_error>
#include <expected>
#include <span>
#include <cstddef>

enum class ReadError {
    Interrupted,
    ResourceUnavailable,
    SystemFailure,
    UnexpectedEof
};

// Ідіоматична C++ обгортка системного виклику read(2) на базі std::span
[[nodiscard]] auto safe_read_span(int fd, std::span<std::byte> destination) 
    -> std::expected<std::size_t, std::error_code> 
{
    std::size_t total_read = 0;

    while (total_read < destination.size()) {
        const auto remaining = destination.subspan(total_read);
        const auto result = ::read(fd, remaining.data(), remaining.size());

        if (result > 0) {
            total_read += static_cast<std::size_t>(result);
            continue;
        }

        if (result == 0) {
            // EOF досягнуто за специфікацією read(2)
            break;
        }

        const int current_error = errno;
        if (current_error == EINTR) {
            // Переривання доставкою сигналу: повторюємо спробу
            continue;
        }

        if (current_error == EAGAIN || current_error == EWOULDBLOCK) {
            if (total_read > 0) {
                return total_read;
            }
            return std::unexpected(std::make_error_code(std::errc::resource_unavailable_try_again));
        }

        return std::unexpected(std::error_code(current_error, std::generic_category()));
    }

    return total_read;
}
