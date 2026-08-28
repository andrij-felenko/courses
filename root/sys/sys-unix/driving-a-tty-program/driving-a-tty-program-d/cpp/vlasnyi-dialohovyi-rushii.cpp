#include <poll.h>
#include <sys/wait.h>
#include <unistd.h>

#include <chrono>
#include <expected>
#include <string>
#include <string_view>
#include <system_error>
#include <vector>

enum class ExpectError {
    Timeout,
    StreamClosed,
    SystemError,
};

std::expected<void, ExpectError> expect_prompt_and_reply(
    int master_fd,
    std::string_view prompt_pattern,
    std::string_view reply,
    std::chrono::milliseconds timeout) 
{
    std::string buffer;
    buffer.reserve(2048);
    char chunk[256];

    struct pollfd pfd{
        .fd = master_fd,
        .events = POLLIN | POLLHUP,
        .revents = 0
    };

    auto start_time = std::chrono::steady_clock::now();

    while (true) {
        auto elapsed = std::chrono::duration_cast<std::chrono::milliseconds>(
            std::chrono::steady_clock::now() - start_time);
        if (elapsed >= timeout) {
            return std::unexpected(ExpectError::Timeout);
        }
        int remaining_ms = static_cast<int>((timeout - elapsed).count());

        int ret = ::poll(&pfd, 1, remaining_ms);
        if (ret < 0) {
            if (errno == EINTR) {
                continue;
            }
            return std::unexpected(ExpectError::SystemError);
        }
        if (ret == 0) {
            return std::unexpected(ExpectError::Timeout);
        }

        if (pfd.revents & (POLLIN | POLLHUP)) {
            ssize_t n = ::read(master_fd, chunk, sizeof(chunk));
            if (n < 0) {
                if (errno == EINTR) {
                    continue;
                }
                if (errno == EIO) {
                    break;
                }
                return std::unexpected(ExpectError::SystemError);
            }
            if (n == 0) {
                break;
            }

            buffer.append(chunk, static_cast<size_t>(n));

            if (buffer.find(prompt_pattern) != std::string::npos) {
                if (::write(master_fd, reply.data(), reply.size()) != static_cast<ssize_t>(reply.size())) {
                    return std::unexpected(ExpectError::SystemError);
                }
                if (::write(master_fd, "\r", 1) != 1) {
                    return std::unexpected(ExpectError::SystemError);
                }
                return {};
            }

            if (buffer.size() > 4096) {
                buffer.erase(0, 2048);
            }
        }
    }

    return std::unexpected(ExpectError::StreamClosed);
}
